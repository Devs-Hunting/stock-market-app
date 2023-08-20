from chatapp.models import Chat
from django.views.generic import DetailView


class ChatView(DetailView):
    model = Chat
    template_name = "chatapp/chat_room.html"
