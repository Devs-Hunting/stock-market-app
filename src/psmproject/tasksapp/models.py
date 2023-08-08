from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import models
from django.utils.translation import gettext_lazy as _
from usersapp.models import Skill


class Task(models.Model):
    """
    This model represents a Task. It includes information such as the title, description,
    expected realization time, budget, client, task status, and the creation and update dates.
    """

    class TaskStatus(models.IntegerChoices):
        OPEN = 0, _("open")  # newly created task, which is visible for contractors and new offers can be added
        ON_HOLD = 1, _(
            "on-hold"
        )  # new task not appearing in search, without possibility to add new offers, no contractor selected
        ON_GOING = 2, _("on-going")  # contractor selected, task in progress
        OBJECTIONS = 3, _("objections")  # task where there is a dispute between client and contractor
        COMPLETED = 4, _("completed")  # task finished and accepted
        CANCELLED = 5, _(
            "cancelled"
        )  # task cancelled by the client, must not be deleted in case of claims from any side

    title = models.CharField(max_length=120)
    description = models.TextField()
    realization_time = models.DateField()
    budget = models.DecimalField(max_digits=6, decimal_places=2)
    skills = models.ManyToManyField(Skill)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.IntegerField(choices=TaskStatus.choices, default=TaskStatus.OPEN)
    # selected_offer = models.OneToOneField(Offer, related_name="in_task", null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Task: {self.title}"

    def __repr__(self):
        return f"<Task id={self.id}, title={self.title}>"

    def delete(self, **kwargs):
        if self.status >= Task.TaskStatus.ON_GOING:
            return
        super().delete(**kwargs)

    @classmethod
    def get_or_warning(cls, id, request):
        try:
            return cls.objects.get(id=id)
        except cls.DoesNotExist:
            messages.warning(request, f"Task with id {id} does not exist")
        return None


ATTACHMENTS_PATH = "attachments/"


def get_upload_path(instance, filename):
    """Generates the file path for the TaskAttachment."""
    return f"{ATTACHMENTS_PATH}tasks/{instance.task.id}/{filename}"


class TaskAttachment(models.Model):
    """
    This model represents a TaskAttachment. It includes information such as the related task,
    the attached file, and the creation and update dates of the attachment.
    """

    MAX_ATTACHMENTS = 10
    ALLOWED_EXTENSIONS = (".txt", ".pdf")
    CONTENT_TYPES = ("text/plain", "application/pdf")
    MAX_UPLOAD_SIZE = 10485760  # 10MB

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    attachment = models.FileField(upload_to=get_upload_path)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attachment: {self.attachment.name} for Task: {self.task.title}"

    def __repr__(self):
        return f"<TaskAttachment id={self.id}, attachment={self.attachment.name}, task_id={self.task.id}>"

    # def get_upload_path(instance, filename):
    #     """Generates the file path for the TaskAttachment."""
    #     return f"attachments/tasks/{instance.task.id}/{filename}"

    def clean(self):
        """
        Custom clean method that checks:
        1. File extension
        2. If the number of attachments for the related task does not exceed limit
        throws an error if any of the conditions is invalid
        """
        if not self.attachment:
            return
        if not str(self.attachment).endswith(TaskAttachment.ALLOWED_EXTENSIONS):
            raise ValidationError("File type not allowed")
        existing_attachments = TaskAttachment.objects.filter(task=self.task).count()
        if existing_attachments >= TaskAttachment.MAX_ATTACHMENTS:
            print("here")
            raise ValidationError("You have reached the maximum number of attachments for this task.")

    def save(self, *args, **kwargs):
        """
        Custom save method that checks for an existing attachment with the same name for
        the related task and deletes it if found before saving the new one.
        """
        file_path = get_upload_path(self, self.attachment)
        existing_attachments = TaskAttachment.objects.filter(task=self.task, attachment=file_path)
        for attachment in existing_attachments:
            attachment.delete()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Deletes attachment from filesystem when corresponding Attachment object is deleted.
        """
        if self.attachment and default_storage.exists(self.attachment.name):
            default_storage.delete(self.attachment.name)
        super().delete(*args, **kwargs)
