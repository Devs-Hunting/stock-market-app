import json
from typing import Dict, List

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chatapp.models import Chat, Message
from chatapp.serializers import message_to_json, messages_to_json
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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
            "request_arbiter": self.request_arbiter,
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

    async def request_arbiter(self, data):
        chat = await Chat.objects.aget(pk=self.chat_id)
        if chat.arbiter_requested:
            info_message = [
                "An arbiter has already been requested.",
                "An arbiter will join the chat as soon as possible.",
            ]
            await self.channel_layer.group_send(
                self.user_group_name,
                {
                    "type": "data_response",
                    "action": data["action"],
                    "info": info_message,
                },
            )
        else:
            chat.arbiter_requested = True
            await chat.asave(update_fields=["arbiter_requested"])
            info_message = ["Arbiter requested!", "An arbiter will join the chat as soon as possible."]
            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    "type": "data_response",
                    "action": data["action"],
                    "info": info_message,
                },
            )

    async def data_response(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message_in_db(self, content: str, author: str) -> Message | Dict[str, List]:
        try:
            author = User.objects.get(username=author)
            chat = Chat.objects.get(pk=self.chat_id)
            msg = Message(chat=chat, author=author, content=content)
            msg.full_clean()
            msg.save()
            return msg
        except ValidationError as ve:
            return {"error": ["Your message could not be sent."] + ve.message_dict["content"]}
        except Exception as e:
            return {"error": ["Your message could not be sent, unexpected error:", str(e)]}
