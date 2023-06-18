from django.conf import settings
from django.db import models


class Chat(models.Model):
    """
    This model represents Chat. There are three related chats: Complaint Chat, Task Chat and Private Chat.
    """


class ComplaintChat(models.Model):
    # complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Complaint Chat - {self.complaint.content}"

    def create_complaint_chat(self, **kwargs):
        complaint_chat = ComplaintChat.objects.create(**kwargs)
        return complaint_chat


class TaskChat(models.Model):
    # task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Task Chat - {self.task.title}"

    def creat_task_chat(self, **kwargs):
        task_chat = TaskChat.objects.create(**kwargs)
        return task_chat


class PrivateChat(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Private Chat - {self.user1.username} - {self.user2.username}"

    def creat_private_chat(self, **kwargs):
        private_chat = PrivateChat.objects.create(**kwargs)
        return private_chat


class Message(models.Model):
    """
    This model represents Message sended by user
    Fields:
    chat (ForeginKey): Associated chat
    author (UserModel): Associated user - author of message
    content (TextField): text of the message
    timestamp (DataTimeFiled): Creation timestamp
    """

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return (
            f"{self.timestamp.strftime('%Y-%m-%d %H:%M')}{self.author}: {self.content}"
        )
