from chatapi.views import MessageListView
from django.urls import path

urlpatterns = [path("room/<int:chat>/messages/", MessageListView.as_view(), name="message-list")]
