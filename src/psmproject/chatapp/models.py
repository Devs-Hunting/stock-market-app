from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Chat(models.Model):
    """
    This model represents Chat. Model is related to Task, Complaint with use GenericForeignKey.
    """

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    def __str__(self) -> str:
        return f"Chat - {self.id}"


class Participant(models.Model):
    """
    This model represents participants in chat with they role.
    Fields:
    chat (ForeginKey): associated chat
    user (userModel): associated user - participant of chat
    role (CharField): role choice for participant
    """

    class RoleChoices(models.TextChoices):
        CLIENT = "CL", ("Client")
        CONTRACTOR = "CO", ("Contractor")
        ARBITER = "AR", ("Arbiter")
        MODERATOR = "MO", ("Moderator")

    chat = models.ForeignKey(Chat, related_name="participants", on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=2, choices=RoleChoices.choices)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()}) in Chat {self.chat.id}"


class Message(models.Model):
    """
    This model represents Message sended by user
    Fields:
    chat (ForeginKey): Associated chat
    author (UserModel): Associated user - author of message
    content (TextField): text of the message
    timestamp (DataTimeFiled): Creation timestamp
    """

    chat = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')}{self.author}: {self.content}"
