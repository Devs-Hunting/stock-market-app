from chatapp.managers import (
    ComplaintChatManager,
    MessageManager,
    PrivateChatManager,
    TaskChatManager,
)
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class RoleChoices(models.TextChoices):
    CLIENT = "CL", ("Client")
    CONTRACTOR = "CO", ("Contractor")
    ARBITER = "AR", ("Arbiter")
    MODERATOR = "MO", ("Moderator")


class Chat(models.Model):
    """
    This model represents Chat. Model is related to Task, Complaint with use GenericForeignKey.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self) -> str:
        return f"Chat - {self.id}"

    @property
    def standard_participants(self):
        return self.participants.filter(~Q(role__in=RoleChoices.values[2:])).values_list("user__username", flat=True)

    @property
    def moderator(self):
        return self.participants.filter(role=RoleChoices.MODERATOR).first()

    def add_participant(self, user, role=None):
        return Participant.objects.create(chat=self, user=user, role=role)

    def has_participant(self, user):
        return self.participants.filter(user=user).first()


class PrivateChat(Chat):
    objects = PrivateChatManager()

    class Meta:
        proxy = True


class TaskChat(Chat):
    objects = TaskChatManager()

    class Meta:
        proxy = True


class ComplaintChat(Chat):
    objects = ComplaintChatManager()

    class Meta:
        proxy = True


class Participant(models.Model):
    """
    This model represents participants in chat with they role.
    Fields:
    chat (ForeginKey): associated chat
    user (userModel): associated user - participant of chat
    role (CharField): role choice for participant
    """

    chat = models.ForeignKey(Chat, related_name="participants", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=2, choices=RoleChoices.choices, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["chat", "user"], name="unique_user_in_chat"),
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_role_valid", check=models.Q(role__in=RoleChoices.values)
            ),
        ]

    def __str__(self):
        return (
            f"{self.user.username} {'(' + self.get_role_display() + ') ' if self.chat.content_type else ''}"
            f"in Chat {self.chat.id}"
        )


class Message(models.Model):
    """
    This model represents Message sended by user
    Fields:
    chat (ForeginKey): Associated chat
    author (UserModel): Associated user - author of message
    content (TextField): text of the message
    timestamp (DataTimeFiled): Creation timestamp
    """

    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE, verbose_name=_("chat"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("author"))
    content = models.CharField(max_length=500, verbose_name=_("content"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("timestamp"))

    objects = MessageManager()

    class Meta:
        ordering = ["-timestamp"]

    @property
    def author_username(self):
        return self.author.username

    @property
    def author_profile_picture_url(self):
        if hasattr(self.author, "profile") and self.author.profile.profile_picture:
            return self.author.profile.profile_picture.url
        return None

    def __str__(self) -> str:
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')}{self.author}: {self.content}"
