from chatapi.views import MessageListApiView
from django.urls import path

urlpatterns = [path("room/<int:chat>/messages/", MessageListApiView.as_view(), name="message-list")]
