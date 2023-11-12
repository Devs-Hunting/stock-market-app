from chatapp.models import (
    Chat,
    ComplaintChat,
    Message,
    Participant,
    PrivateChat,
    TaskChat,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Max
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView

User = get_user_model()


class OpenPrivateChatView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        chat_id = self.get_private_chat_id(**kwargs)
        return reverse("chat", kwargs={"pk": chat_id})

    @staticmethod
    def get_contact_from_url(**kwargs):
        return User.objects.get(pk=kwargs["user_id"])

    def get_private_chat_id(self, **kwargs):
        contact_user = self.get_contact_from_url(**kwargs)
        current_user = self.request.user
        with transaction.atomic():
            chat, created = (
                PrivateChat.objects.filter(participants__user=contact_user).filter(participants__user=current_user)
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


class ChatListView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = "chatapp/chat_list.html"
    list_title = "All chats"
    paginate_by = 5

    def get_context_data(self, **kwargs):
        kwargs["list_title"] = self.list_title
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return (
            queryset.filter(participants__user=self.request.user, messages__isnull=False)
            .annotate(last_message_at=Max("messages__timestamp"))
            .order_by("-last_message_at")
        )


class PrivateChatListView(ChatListView):
    model = PrivateChat
    list_title = "Private chats"


class TaskChatListView(ChatListView):
    model = TaskChat
    list_title = "Task chats"


class ComplaintChatListView(ChatListView):
    model = ComplaintChat
    list_title = "Complaint chats"
