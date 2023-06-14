from django.conf import settings
from django.db import models


class Chat(models.Model):
    """
    This model represents Chat. There are two related chats: Complaint Chat and Project/Task Chat.
    """


class ComplaintChat(models.Model):
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE)
    # complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Chat - Complaint {self.complaint.content}"


class ProjectChat(models.Model):
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE)
    # project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Chat - Project {self.project.title}"


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
        return super().__str__()
