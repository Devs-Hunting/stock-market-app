import json
from typing import Dict, List

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chatapp.exceptions import DeleteMessageRightsMissing, MessageAuthorNotInChat
from chatapp.models import Chat, Message, Participant, RoleChoices
from chatapp.serializers import message_to_json, messages_to_json
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from usersapp.helpers import has_group

GROUP_TO_ROLE = {settings.GROUP_NAMES["MODERATOR"]: RoleChoices.MODERATOR}


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_id = None
        self.chat_group_name = None
        self.user = None
        self.user_group_name = None

    @property
    def do_action(self):
        return {
            "send_new_message": self.send_new_message,
            "fetch_messages": self.fetch_messages,
            "join_chat": self.join_chat,
            "leave_chat": self.leave_chat,
            "delete_message": self.delete_message,
        }

    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["pk"]
        self.chat_group_name = f"chat_{self.chat_id}"
        self.user = self.scope["url_route"]["kwargs"]["username"]
        self.user_group_name = f"{self.chat_group_name}_username_{self.user}"
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        await self.do_action[text_data_json["action"]](text_data_json)

    async def send_new_message(self, data):
        content = data["content"]
        author = data["author"]
        new_message = await self.save_message_in_db(content, author)
        if isinstance(new_message, Message):
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    "type": "data_response",
                    "action": data["action"],
                    "message": await message_to_json(new_message),
                },
            )
        else:
            await self.channel_layer.group_send(
                self.user_group_name,
                {
                    "type": "data_response",
                    "action": "throw_error",
                }
                | new_message,
            )

    async def fetch_messages(self, data):
        chat_connection_timestamp = data["chat_connection_timestamp"]
        visible_messages = data["visible_messages"]
        messages = await database_sync_to_async(Message.objects.get_chat_message_history)(
            chat_id=self.chat_id, max_datetime=chat_connection_timestamp, visible_messages=visible_messages
        )
        await self.channel_layer.group_send(
            self.user_group_name,
            {
                "type": "data_response",
                "action": data["action"],
                "messages": await messages_to_json(messages),
            },
        )

    async def delete_message(self, data):
        msg_id = data["message_id"]
        requester = data["requester"]
        response = await self.delete_message_from_db(msg_id, requester)
        if "error" in response.keys():
            await self.channel_layer.group_send(
                self.user_group_name,
                {
                    "type": "data_response",
                    "action": "throw_error",
                }
                | response,
            )
        else:
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    "type": "data_response",
                    "action": data["action"],
                    "notification": "Message has been removed.",
                },
            )

    async def join_chat(self, data):
        await self.create_new_participant(data["user"])
        await self.channel_layer.group_send(
            self.user_group_name,
            {"type": "data_response", "action": data["action"], "notification": "You have joined the chat."},
        )

    async def leave_chat(self, data):
        await self.remove_participant(data["user"])
        await self.channel_layer.group_send(
            self.user_group_name,
            {"type": "data_response", "action": data["action"], "notification": "You have left the chat."},
        )

    async def data_response(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def create_new_participant(self, username):
        joining_user = User.objects.get(username=username)
        user_role = GROUP_TO_ROLE[joining_user.groups.all().first().name]
        chat = Chat.objects.get(pk=self.chat_id)
        return chat.add_participant(joining_user, role=user_role)

    @database_sync_to_async
    def remove_participant(self, username):
        leaving_user = User.objects.get(username=username)
        chat = Chat.objects.get(pk=self.chat_id)
        participant = Participant.objects.get(chat=chat, user=leaving_user)
        participant.delete()

    @database_sync_to_async
    def save_message_in_db(self, content: str, author: str) -> Message | Dict[str, List]:
        try:
            author = User.objects.get(username=author)
            chat = Chat.objects.get(pk=self.chat_id)
            if not chat.has_participant(author):
                raise MessageAuthorNotInChat
            msg = Message(chat=chat, author=author, content=content)
            msg.full_clean()
            msg.save()
            return msg
        except MessageAuthorNotInChat:
            return {"error": ["You are not a participant to this chat."]}
        except ValidationError as ve:
            return {"error": ["Your message could not be sent."] + ve.message_dict["content"]}
        except Exception as e:
            return {"error": ["Your message could not be sent, unexpected error:", str(e)]}

    @database_sync_to_async
    def delete_message_from_db(self, msg_id: int, requester: str) -> Dict:
        try:
            message = Message.objects.get(pk=msg_id)
            user_requester = User.objects.get(username=requester)
            if (
                message.author != user_requester
                and not message.chat.has_participant(user_requester)
                and not has_group(user_requester, settings.GROUP_NAMES.get("MODERATOR"))
            ):
                raise DeleteMessageRightsMissing
            message.delete()
            return {"notification": "Message deleted."}
        except DeleteMessageRightsMissing:
            return {"error": ["You must be author of this message or a Moderator to be able to delete this message"]}
        except Exception as e:
            return {"error": ["Your message could not be deleted, unexpected error:", str(e)]}
