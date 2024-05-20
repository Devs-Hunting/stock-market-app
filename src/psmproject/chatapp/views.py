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
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db import transaction
from django.db.models import OuterRef, Q, Subquery
from django.http import Http404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, ListView, RedirectView
from django.views.generic.edit import FormMixin
from usersapp.helpers import has_group

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
                _(
                    "We had trouble to find the user you are trying to contact.\n"
                    "Please try later or contact the administrator if the issue persists"
                )
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
                _("We are not able to open chat, we found duplicates of this chat.\nPlease contact the administrator")
            )
        return chat


class ChatView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Chat
    template_name = "chatapp/chat_room.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["message_max_length"] = Message._meta.get_field("content").max_length
        context["user_has_moderator_role"] = has_group(self.request.user, settings.GROUP_NAMES.get("MODERATOR"))
        return context

    def test_func(self):
        return self.request.user in [
            participant.user for participant in self.get_object().participants.all()
        ] or has_group(self.request.user, settings.GROUP_NAMES.get("MODERATOR"))


class ChatListView(LoginRequiredMixin, FormMixin, ListView):
    model = Chat
    context_object_name = "chats"
    template_name = "chatapp/chat_list.html"
    list_title = _("All chats")
    paginate_by = 5
    form_class = ChatSearchForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["list_title"] = self.list_title
        context["form"] = self.get_form_class()(self.request.GET)
        return context

    def search_condition(self, participant):
        return Q(
            participants__in=Participant.objects.filter(
                Q(user__username__icontains=participant) & ~Q(user=self.request.user)
            )
        )

    def get_queryset(self):
        queryset = self.build_queryset_for_list_view(super().get_queryset())
        form = self.get_form_class()(self.request.GET)
        if form.is_valid() and form.cleaned_data["contact_name"]:
            participant = form.cleaned_data["contact_name"]
            queryset = queryset.filter(self.search_condition(participant))
        return queryset

    @property
    def _last_message_subquery(self):
        return (
            Message.objects.filter(chat=OuterRef("pk"))
            .order_by("-timestamp")
            .values("timestamp", "author__username", "content")
        )

    @property
    def _contact_subquery(self):
        return Participant.objects.filter(
            Q(chat=OuterRef("pk")) & ~(Q(user=self.request.user) | Q(role__in=RoleChoices.values[2:]))
        )

    @property
    def _last_message_annotation(self):
        return {
            "last_message_at": Subquery(self._last_message_subquery.values("timestamp")[:1]),
            "last_message_author": Subquery(self._last_message_subquery.values("author__username")[:1]),
            "last_message_content": Subquery(self._last_message_subquery.values("content")[:1]),
        }

    def build_queryset_for_list_view(self, queryset):
        return (
            queryset.filter(participants__user=self.request.user, messages__isnull=False)
            .annotate(**self._last_message_annotation)
            .annotate(contact=Subquery(self._contact_subquery.values("user__username")[:1]))
            .order_by("-last_message_at")
            .distinct()
        )


class PrivateChatListView(ChatListView):
    model = PrivateChat
    list_title = _("Private chats")


class TaskChatListView(ChatListView):
    model = TaskChat
    list_title = _("Task chats")


class ComplaintChatListView(ChatListView):
    model = ComplaintChat
    list_title = _("Complaint chats")


class ChatListModeratorView(UserPassesTestMixin, ChatListView):
    paginate_by = 10

    def build_queryset_for_list_view(self, queryset):
        return (
            queryset.filter(messages__isnull=False)
            .annotate(**self._last_message_annotation)
            .order_by("-last_message_at")
            .distinct()
        )

    def test_func(self):
        return self.request.user.groups.filter(name=settings.GROUP_NAMES.get("MODERATOR")).exists()


class WaitingForModerationChatListModeratorView(ChatListModeratorView):
    list_title = _("Chats waiting for moderation")

    def build_queryset_for_list_view(self, queryset):
        return (
            queryset.filter(~Q(participants__role=RoleChoices.MODERATOR) & Q(messages__isnull=False))
            .annotate(**self._last_message_annotation)
            .order_by("pk")
            .distinct()
        )


class ModeratedChatListModeratorView(ChatListModeratorView):
    list_title = _("My moderated chats")

    def build_queryset_for_list_view(self, queryset):
        return (
            queryset.filter(Q(participants__user=self.request.user) & Q(messages__isnull=False))
            .annotate(**self._last_message_annotation)
            .order_by("pk")
            .distinct()
        )
