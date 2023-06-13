from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()


class Task(models.Model):
    class TaskStatus(models.IntegerChoices):
        OPEN = 0, _("open")
        CLOSED = 1, _("closed")
        ON_GOING = 2, _("on-going")
        HOLD = 3, _("hold")
        COMPLETED = 4, _("completed")
        CANCELLED = 5, _("cancelled")

    title = models.CharField(max_length=120)
    description = models.TextField()
    realization_time = models.DateField()
    budget = models.FloatField()
    client = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    status = models.IntegerField(
        choices=TaskStatus.choices, default=TaskStatus.OPEN
    )
    # selected_offer = models.OneToOneField(Offer, related_name="in_task", null=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class TaskAttachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments")
    attachment = models.FileField(upload_to="attachments/")
    updated = models.DateTimeField(auto_now=True)
