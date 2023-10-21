from chatapp.views import ChatView, OpenPrivateChatView
from django.urls import path

urlpatterns = [
    path("room/<pk>/", ChatView.as_view(), name="chat"),
    path("open_chat_room/<int:user_id>/", OpenPrivateChatView.as_view(), name="open-chat"),
]
