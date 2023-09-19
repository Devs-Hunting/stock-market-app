import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import models


class Complaint(models.Model):
    """
    This model represents a Complaint. Is related to Solution.
    It includes information such as: content, arbiter (user in appropriate role), closed,
    created_at, updated_at.
    Complaint could be closed by arbiter if complaint process is finished.
    """

    content = models.TextField()
    arbiter = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Complaint id={self.id} for Solution id={self.solution.id}, status: {self.closed}."

    def __repr__(self) -> str:
        return f"<Complaint id={self.id}, status: {self.closed}>"


class Solution(models.Model):
    """
    This model represents a Solution. Is related to a Complaint and a Offer.
    It includes information such as: description, submitted, accepted, end, updated_at.
    """

    description = models.TextField()
    submitted = models.BooleanField(default=True)
    accepted = models.BooleanField(default=False)
    end = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    complaint = models.OneToOneField(Complaint, related_name="solution", null=True, on_delete=models.SET_NULL)

    def __str__(self) -> str:
        return f"Solution id={self.id} for Offer id={self.offer.id} - status: {self.accepted}"

    def __repr__(self) -> str:
        return f"<Solution id={self.id} - status: {self.accepted}>"


class Offer(models.Model):
    """
    This model represents a Offer. Is related to Task (as offer and selected offer), Solution and Contractor.
    It includes information such as: description, expected realization time, budget, created_at.
    Offer could be accepted then it will be selected offer.
    If the offer is accepted then will be made a solution for it and
    when the solution is accepted then the offer should be paid.
    """

    description = models.TextField()
    solution = models.OneToOneField(Solution, related_name="offer", blank=True, null=True, on_delete=models.SET_NULL)
    task = models.ForeignKey("tasksapp.Task", related_name="offers", null=True, on_delete=models.CASCADE)
    realization_time = models.DateField()
    budget = models.DecimalField(max_digits=8, decimal_places=2)
    contractor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Offer by {self.contractor}"

    def __repr__(self) -> str:
        return f"<Offer id={self.id} for Task id={self.task.id}, contractor={self.contractor}>"

    def clean(self) -> None:
        super().clean()
        if self.budget <= 0:
            raise ValidationError("The budget must be greater than 0")
        if self.realization_time <= datetime.date.today():
            raise ValidationError("The realization time must be in the future")


ATTACHMENTS_PATH = "attachments/"  # TODO przenieść do settings??


def get_upload_path(instance, filename):
    """
    Generates the file path for the Attachment.
    """
    if isinstance(instance, Solution):
        return f"{ATTACHMENTS_PATH}solution/{instance.solution.id}/{filename}"
    elif isinstance(instance, Complaint):
        return f"{ATTACHMENTS_PATH}complaint/{instance.complaint.id}/{filename}"


class Attachment(models.Model):  # TODO - refactoring of methods in attachment class: issue [DEV-86]
    MAX_ATTACHMENTS = 10
    ALLOWED_EXTENSIONS = (".txt", ".pdf")
    CONTENT_TYPES = ("text/plain", "application/pdf")
    MAX_UPLOAD_SIZE = 10485760  # 10MB

    attachment = models.FileField(upload_to=get_upload_path)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def clean(self):
        """
        Custom clean method that checks:
        1. File extension
        """
        if not self.attachment:
            return
        if not str(self.attachment).endswith(Attachment.ALLOWED_EXTENSIONS):
            raise ValidationError("File type not allowed")
        self.validation_max_number_attachments(self.__class__)

    def delete(self, *args, **kwargs):
        """
        Deletes attachment from filesystem when corresponding Attachment object is deleted.
        """
        if self.attachment and default_storage.exists(self.attachment.name):
            default_storage.delete(self.attachment.name)
        super().delete(*args, **kwargs)

    def choosing_existing_attachments(self):
        if self.__class__ == ComplaintAttachment:
            return self.__class__.objects.filter(complaint=self.complaint)
        elif self.__class__ == SolutionAttachment:
            return self.__class__.objects.filter(solution=self.solution)

    def validation_max_number_attachments(self, model_type):
        existing_attachments = self.choosing_existing_attachments(model_type)
        if existing_attachments.count() >= model_type.MAX_ATTACHMENTS:
            new_file_path = get_upload_path(self, self.attachment)
            will_overwrite = existing_attachments.filter(attachment=new_file_path).exists()
            if not will_overwrite:
                raise ValidationError("You have reached the maximum number of attachments for this complaint.")

    def save(self, *args, **kwargs):
        """
        Custom save method that checks for an existing attachment with the same name for
        the related task and deletes it if found before saving the new one.
        """
        file_path = get_upload_path(self, self.attachment)
        existing_attachments = self.choosing_existing_attachments(self.__class__)
        existing_attachments_with_same_name = existing_attachments.objects.filter(attachment=file_path)
        for attachment in existing_attachments_with_same_name:
            attachment.delete()


class SolutionAttachment(Attachment):
    solution = models.ForeignKey(Solution, related_name="attachment", null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f"Solution Attachment: {self.attachment.name} for Solution: {self.solution.id}"

    def __repr__(self):
        return f"<Solution Attachment id={self.id}, attachment={self.attachment.name}, solution_id={self.solution.id}>"


class ComplaintAttachment(Attachment):
    complaint = models.ForeignKey(Complaint, related_name="attachment", null=True, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"Complaint Attachment: {self.attachment.name} for Complaint: {self.complaint.id}"

    def __repr__(self) -> str:
        return (
            f"<Complaint Attachment id={self.id}, attachment={self.attachment.name}, complaint_id={self.complaint.id}>"
        )
