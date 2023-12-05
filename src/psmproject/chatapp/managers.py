from django.db import models
from tasksapp.models import Complaint, Task


class PrivateChatManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(content_type=None)


class TaskChatManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(content_type__model=Task._meta.model_name)


class ComplaintChatManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(content_type__model=Complaint._meta.model_name)


class MessageManager(models.Manager):
    def get_chat_message_history(self, *, chat_id, max_datetime, visible_messages):
        upper = visible_messages
        lower = visible_messages - 10
        messages = self.filter(chat=chat_id, timestamp__lte=max_datetime)[lower:upper]
        return messages
