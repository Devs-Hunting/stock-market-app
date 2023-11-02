from chatapp.models import Chat, Message, Participant
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.views.generic import DetailView, RedirectView

User = get_user_model()


class OpenPrivateChatView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        chat_id = self.get_private_chat(**kwargs)
        return reverse("chat", kwargs={"pk": chat_id})

    @staticmethod
    def get_contact_from_url(**kwargs):
        return User.objects.get(pk=kwargs["user_id"])

    def get_private_chat(self, **kwargs):
        contact_user = self.get_contact_from_url(**kwargs)
        current_user = self.request.user
        chat, created = (
            Chat.objects.filter(object_id=None)
            .filter(participants__user=contact_user)
            .filter(participants__user=current_user)
        ).get_or_create()
        if created:
            Participant.objects.create(chat=chat, user=contact_user)
            Participant.objects.create(chat=chat, user=current_user)
        return chat.id


class ChatView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Chat
    template_name = "chatapp/chat_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message_max_length"] = Message._meta.get_field("content").max_length
        return context

    def test_func(self):
        return self.request.user in [participant.user for participant in self.get_object().participants.all()]
