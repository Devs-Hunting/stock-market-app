import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chatapp.models import Chat, Message
from chatapp.serializers import message_to_json, messages_to_json
from django.contrib.auth.models import User


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_id = None
        self.room_group_name = None
        self.user = None
        self.user_group_name = None

    @property
    def do_action(self):
        return {
            "send_new_message": self.send_new_message,
            "fetch_messages": self.fetch_messages,
        }

    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = f"chat_{self.chat_id}"
        self.user = self.scope["url_route"]["kwargs"]["username"]
        self.user_group_name = f"{self.room_group_name}_username_{self.user}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.channel_layer.group_add(self.user_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        await self.do_action[text_data_json["action"]](text_data_json)

    async def send_new_message(self, data):
        content = data["content"]
        author = data["author"]
        new_message = await self.save_message_in_db(content, author)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "action": data["action"],
                "message": await message_to_json(new_message),
            },
        )

    async def fetch_messages(self, data):
        action = data["action"]
        chat_connection_timestamp = data["chat_connection_timestamp"]
        visible_messages = data["visible_messages"]
        messages = await database_sync_to_async(Message.objects.get_chat_message_history)(
            chat_id=self.chat_id, max_datetime=chat_connection_timestamp, visible_messages=visible_messages
        )
        await self.channel_layer.group_send(
            self.user_group_name,
            {
                "type": "chat.message",
                "action": action,
                "messages": await messages_to_json(messages),
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message_in_db(self, content: str, author: str) -> Message:
        author = User.objects.get(username=author)
        chat = Chat.objects.get(pk=self.chat_id)
        msg = Message(chat=chat, author=author, content=content)
        msg.full_clean()
        msg.save()
        return msg
