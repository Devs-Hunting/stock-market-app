from chatapp.models import Chat, Message
from django.views.generic import DetailView


class ChatView(DetailView):
    model = Chat
    template_name = "chatapp/chat_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message_max_length"] = Message._meta.get_field("content").max_length
        return context
