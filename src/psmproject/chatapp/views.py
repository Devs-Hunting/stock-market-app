from chatapp.models import Chat, Message
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView


class ChatView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Chat
    template_name = "chatapp/chat_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message_max_length"] = Message._meta.get_field("content").max_length
        return context

    def test_func(self):
        return self.request.user in [participant.user for participant in self.get_object().participants.all()]
