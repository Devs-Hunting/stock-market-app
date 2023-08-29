import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chatapp.models import Chat, Message
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils.formats import time_format


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json["content"]
        author = text_data_json["author"]
        new_message = await self.save_message_in_db(content, author)
        timestamp = time_format(new_message.timestamp)
        author_picture = await self.get_picture_url_by_username(author)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "content": content,
                "author": author,
                "picture": author_picture,
                "timestamp": timestamp,
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_picture_url_by_username(self, username: str) -> str | None:
        try:
            return User.objects.get(username=username).profile.profile_picture.url
        except ObjectDoesNotExist:
            return None

    @database_sync_to_async
    def save_message_in_db(self, content: str, author: str) -> Message:
        author = User.objects.get(username=author)
        chat = Chat.objects.get(pk=self.room_id)
        msg = Message(chat=chat, author=author, content=content)
        msg.full_clean()
        msg.save()
        return msg
