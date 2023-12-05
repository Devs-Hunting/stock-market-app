from chatapp.views import (
    ChatListView,
    ChatView,
    ComplaintChatListView,
    OpenPrivateChatView,
    PrivateChatListView,
    TaskChatListView,
)
from django.urls import path

urlpatterns = [
    path("room/<pk>/", ChatView.as_view(), name="chat"),
    path("open_chat_room/<int:user_id>/", OpenPrivateChatView.as_view(), name="open-chat"),
    path("chat_list/private/", PrivateChatListView.as_view(), name="private-chats"),
    path("chat_list/task/", TaskChatListView.as_view(), name="task-chats"),
    path("chat_list/complaint/", ComplaintChatListView.as_view(), name="complaint-chats"),
    path("chat_list/all/", ChatListView.as_view(), name="all-chats"),
]
