import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


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
        message = text_data_json["message"]
        author = text_data_json["author"]
        author_picture = await self.get_picture_url_by_username(author)
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat.message", "message": message, "author": author, "picture": author_picture},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_picture_url_by_username(self, username: str) -> str | None:
        try:
            return User.objects.get(username=username).profile.profile_picture.url
        except ObjectDoesNotExist:
            return None
