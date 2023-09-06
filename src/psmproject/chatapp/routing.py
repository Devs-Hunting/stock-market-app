from chatapp.consumers import ChatConsumer
from django.urls import path

websocket_urlpatterns = [
    path("ws/chat/room/<pk>/user/<username>/", ChatConsumer.as_asgi()),
]
