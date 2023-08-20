import json

from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth.models import User


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        author = text_data_json["author"]
        author_picture = User.objects.get(username=author).profile.profile_picture.url

        self.send(text_data=json.dumps({"message": message, "author": author, "picture": author_picture}))
