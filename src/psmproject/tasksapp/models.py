from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files.storage import default_storage
from django.db import models
from django.utils.translation import gettext_lazy as _


class Task(models.Model):
    """
    This model represents a Task. It includes information such as the title, description,
    expected realization time, budget, client, task status, and the creation and update dates.
    """

    class TaskStatus(models.IntegerChoices):
        OPEN = 0, _("open")
        CLOSED = 1, _("closed")
        ON_GOING = 2, _("on-going")
        OBJECTIONS = 3, _("objections")
        COMPLETED = 4, _("completed")
        CANCELLED = 5, _("cancelled")

    title = models.CharField(max_length=120)
    description = models.TextField()
    realization_time = models.DateField()
    budget = models.DecimalField(max_digits=6, decimal_places=2)
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
        except ObjectDoesNotExist:
            messages.warning(request, f"Task with id {id} does not exist")
        return None


def get_upload_path(instance, filename):
    """Generates the file path for the TaskAttachment."""
    return f"attachments/tasks/{instance.task.id}/{filename}"


class TaskAttachment(models.Model):
    """
    This model represents a TaskAttachment. It includes information such as the related task,
    the attached file, and the creation and update dates of the attachment.
    """

    MAX_ATTACHMENTS = 10

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    attachment = models.FileField(upload_to=get_upload_path)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attachment: {self.attachment.name} for Task: {self.task.title}"

    def __repr__(self):
        return f"<TaskAttachment id={self.id}, attachment={self.attachment.name}, task_id={self.task.id}>"

    def clean(self):
        """
        Custom clean method that checks the number of attachments for the related task and
        throws an error if the limit is exceeded.
        """
        existing_attachments = TaskAttachment.objects.filter(task=self.task).count()
        if existing_attachments >= TaskAttachment.MAX_ATTACHMENTS:
            print("here")
            raise ValidationError(
                "You have reached the maximum number of attachments for this task."
            )

    def save(self, *args, **kwargs):
        """
        Custom save method that checks for an existing attachment with the same name for
        the related task and deletes it if found before saving the new one.
        """
        file_path = get_upload_path(self, self.attachment)
        existing = TaskAttachment.objects.filter(task=self.task, attachment=file_path)
        for existing_file in existing:
            existing_file.delete()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Deletes attachment from filesystem when corresponding Attachment object is deleted.
        """
        print(self.attachment)
        if self.attachment:
            if default_storage.exists(self.attachment.name):
                default_storage.delete(self.attachment.name)
        super().delete(*args, **kwargs)
