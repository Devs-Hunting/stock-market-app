from chatapp.forms import ChatSearchForm
from chatapp.models import (
    Chat,
    ComplaintChat,
    Message,
    Participant,
    PrivateChat,
    RoleChoices,
    TaskChat,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import transaction
from django.db.models import OuterRef, Q, Subquery
from django.http import Http404
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView
from django.views.generic.edit import FormMixin

User = get_user_model()


class OpenPrivateChatView(LoginRequiredMixin, RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        chat = self.get_private_chat(**kwargs)
        if isinstance(chat, Chat):
            return reverse("chat", kwargs={"pk": chat.id})
        return reverse("chat-error", kwargs={"error_message": chat})

    @staticmethod
    def get_contact_from_url(**kwargs):
        try:
            return User.objects.get(pk=kwargs["user_id"])
        except ObjectDoesNotExist:
            raise Http404(
                "We had trouble to find the user you are trying to contact.\n"
                "Please try later or contact the administrator if the issue persists"
            )

    def get_private_chat(self, **kwargs):
        contact_user = self.get_contact_from_url(**kwargs)
        current_user = self.request.user
        try:
            with transaction.atomic():
                chat, created = (
                    PrivateChat.objects.filter(participants__user=contact_user).filter(participants__user=current_user)
                ).get_or_create()
                if created:
                    Participant.objects.create(chat=chat, user=contact_user)
                    Participant.objects.create(chat=chat, user=current_user)
        except MultipleObjectsReturned:
            raise Http404(
                "We are not able to open chat, we found duplicates of this chat.\nPlease contact the administrator"
            )
        return chat


class ChatView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Chat
    template_name = "chatapp/chat_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message_max_length"] = Message._meta.get_field("content").max_length
        return context

    def test_func(self):
        return self.request.user in [participant.user for participant in self.get_object().participants.all()]


class ChatListView(LoginRequiredMixin, FormMixin, ListView):
    model = Chat
    context_object_name = "chats"
    template_name = "chatapp/chat_list.html"
    list_title = "All chats"
    paginate_by = 5
    form_class = ChatSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_title"] = self.list_title
        context["form"] = self.get_form_class()(self.request.GET)
        return context

    def get_queryset(self):
        queryset = self.build_queryset_for_list_view(super().get_queryset())
        form = self.get_form_class()(self.request.GET)
        if form.is_valid() and form.cleaned_data["contact_name"]:
            participant = form.cleaned_data["contact_name"]
            queryset = queryset.filter(contact__icontains=participant)
        return queryset

    def build_queryset_for_list_view(self, queryset):
        last_message_sq = (
            Message.objects.filter(chat=OuterRef("pk"))
            .order_by("-timestamp")
            .values("timestamp", "author__username", "content")[:1]
        )
        contact_sq = Participant.objects.filter(
            Q(chat=OuterRef("pk")) & ~(Q(user=self.request.user) | Q(role__in=RoleChoices.values[2:]))
        )
        return (
            queryset.filter(participants__user=self.request.user, messages__isnull=False)
            .annotate(
                last_message_at=Subquery(last_message_sq.values("timestamp")),
                last_message_author=Subquery(last_message_sq.values("author__username")),
                last_message_content=Subquery(last_message_sq.values("content")),
            )
            .annotate(contact=Subquery(contact_sq.values("user__username")))
            .order_by("-last_message_at")
            .distinct()
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
