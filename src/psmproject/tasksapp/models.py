from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from usersapp.models import Skill


class Task(models.Model):
    """
    This model represents a Task. It includes information such as the title, description,
    days_to_complete, budget, client, task status, and the creation and update dates.
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

    title = models.CharField(max_length=120, verbose_name=_("title"))
    description = models.TextField(verbose_name=_("description"))
    days_to_complete = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name=_("days to complete")
    )
    budget = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("budget"))
    skills = models.ManyToManyField(Skill, verbose_name=_("skills"))
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("client"))
    status = models.IntegerField(choices=TaskStatus.choices, default=TaskStatus.OPEN, verbose_name=_("status"))
    selected_offer = models.OneToOneField(
        "tasksapp.Offer",
        related_name="in_task",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("selected offer"),
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("updated"))

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


class Complaint(models.Model):
    """
    This model represents a Complaint. Is related to Task.
    It includes information such as: content, arbiter (user in appropriate role), closed,
    created_at, updated_at.
    Complaint could be closed by arbiter if complaint process is finished.
    """

    task = models.ForeignKey(Task, related_name="complaints", on_delete=models.CASCADE)
    complainant = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="complaints_made", on_delete=models.CASCADE)
    content = models.TextField()
    arbiter = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="complaints_to_judge", null=True, on_delete=models.SET_NULL
    )
    closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["task", "complainant"],
                name="unique_task_user",
                violation_error_message="cannot create second complaint for this task",
            )
        ]

    def __str__(self) -> str:
        return f"Complaint id={self.id} for Task id={self.task.id}, from {self.complainant}, status: {self.closed}."

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

    def __str__(self) -> str:
        return f"Solution id={self.id} for Offer id={self.offer.id} - accepted: {self.accepted}"

    def __repr__(self) -> str:
        return f"<Solution id={self.id} - accepted: {self.accepted}>"


class Payment(models.Model):
    """
    Payment model with one-to-one relationship with Offer model.
    Total amount field is the total amount that should be paid for task.
    Fee percentage and advance percentage fields have default value that will settle values for fields amount due to
    contractor as well as advance amount.
    Advance received field informs if client send amount for advance.
    Total amount received field informs if client paid total amount of payment.
    Contractor paid field informs if total amount was paid to contractor.
    """

    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    fee_percentage = models.PositiveIntegerField(default=15, validators=[MaxValueValidator(15)])
    advance_percentage = models.PositiveIntegerField(default=50, validators=[MaxValueValidator(100)])
    advance_received = models.BooleanField(default=False)
    total_amount_received = models.BooleanField(default=False)
    contractor_paid = models.BooleanField(default=False)

    @property
    def service_fee(self):
        return (self.total_amount * self.fee_percentage) / 100

    @property
    def amount_due_to_contractor(self):
        return self.total_amount - self.service_fee

    @property
    def advance_amount(self):
        return (self.total_amount * self.advance_percentage) / 100

    def __str__(self):
        return f"Payment: {self.total_amount}{' - COMPLETED' if self.contractor_paid else ''}"


class Offer(models.Model):
    """
    This model represents a Offer. Is related to Task (as offer and selected offer), Solution and Contractor.
    It includes information such as: description, days to complete, expected realization time, budget, created_at.
    Offer could be accepted then it will be selected offer.
    If the offer is accepted then will be made a solution for it and
    when the solution is accepted then the offer should be paid.
    """

    description = models.TextField(verbose_name=_("description"))
    solution = models.OneToOneField(
        Solution, related_name="offer", blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("solution")
    )
    task = models.ForeignKey(Task, related_name="offers", null=True, on_delete=models.CASCADE, verbose_name=_("task"))
    days_to_complete = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name=_("days to complete")
    )
    realization_time = models.DateField(null=True, blank=True, verbose_name=_("realization time"))
    budget = models.DecimalField(max_digits=8, decimal_places=2, verbose_name=_("budget"))
    contractor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("contractor"))
    accepted = models.BooleanField(default=False, verbose_name=_("accepted"))
    payment = models.OneToOneField(
        Payment, related_name="offer", null=True, blank=True, on_delete=models.CASCADE, verbose_name=_("payment")
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"))

    def __str__(self) -> str:
        prefix = _("Offer by")
        return f"{prefix} {self.contractor}"

    def __repr__(self) -> str:
        return f"<Offer id={self.id} for Task id={self.task.id}, contractor={self.contractor}>"

    def clean(self) -> None:
        super().clean()
        if self.budget <= 0:
            raise ValidationError("The budget must be greater than 0")


ATTACHMENTS_PATH = "attachments/"  # TODO przenieść do settings??


def get_upload_path(instance, filename):
    """
    Generates the file path for the Attachment.
    """
    if isinstance(instance, TaskAttachment):
        return f"{ATTACHMENTS_PATH}tasks/{instance.task.id}/{filename}"
    elif isinstance(instance, SolutionAttachment):
        return f"{ATTACHMENTS_PATH}solutions/{instance.solution.id}/{filename}"
    elif isinstance(instance, ComplaintAttachment):
        return f"{ATTACHMENTS_PATH}complaints/{instance.complaint.id}/{filename}"


class Attachment(models.Model):  # TODO - refactoring of methods in attachment class: issue [DEV-86]
    MAX_ATTACHMENTS = 10
    ALLOWED_EXTENSIONS = (".txt", ".pdf")
    CONTENT_TYPES = ("text/plain", "application/pdf")
    MAX_UPLOAD_SIZE = 10485760  # 10MB

    attachment = models.FileField(upload_to=get_upload_path, verbose_name=_("attachment"))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("updated"))

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

    def choosing_existing_attachments(self, model_type):
        if model_type == TaskAttachment:
            return self.__class__.objects.filter(task=self.task)
        elif model_type == ComplaintAttachment:
            return self.__class__.objects.filter(complaint=self.complaint)
        elif model_type == SolutionAttachment:
            return self.__class__.objects.filter(solution=self.solution)
        else:
            return SolutionAttachment.objects.filter(solution=self.solution)

    def validation_max_number_attachments(self, model_type):
        existing_attachments = self.choosing_existing_attachments(model_type)
        if existing_attachments.count() >= self.MAX_ATTACHMENTS:
            new_file_path = get_upload_path(self, self.attachment)
            will_overwrite = existing_attachments.filter(attachment=new_file_path).exists()
            if not will_overwrite:
                raise ValidationError("You have reached the maximum number of attachments.")

    def save(self, *args, **kwargs):
        """
        Custom save method that checks for an existing attachment with the same name for
        the related task and deletes it if found before saving the new one.
        """
        file_path = get_upload_path(self, self.attachment)
        existing_attachments = self.choosing_existing_attachments(self.__class__)
        existing_attachments_with_same_name = existing_attachments.filter(attachment=file_path)
        for attachment in existing_attachments_with_same_name:
            attachment.delete()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.attachment.name


class TaskAttachment(Attachment):
    """
    This model represents a TaskAttachment. It includes information such as the related task,
    the attached file, and the creation and update dates of the attachment.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="attachments", verbose_name=_("task"))

    def __repr__(self):
        return f"<TaskAttachment id={self.id}, attachment={self.attachment.name}, task_id={self.task.id}>"


class SolutionAttachment(Attachment):
    solution = models.ForeignKey(
        Solution, related_name="attachments", on_delete=models.CASCADE, verbose_name=_("solution")
    )

    def __repr__(self):
        return f"<Solution Attachment id={self.id}, attachment={self.attachment.name}, solution_id={self.solution.id}>"


class ComplaintAttachment(Attachment):
    complaint = models.ForeignKey(
        Complaint, related_name="attachments", on_delete=models.CASCADE, verbose_name=_("complaint")
    )

    def __repr__(self) -> str:
        return (
            f"<Complaint Attachment id={self.id}, attachment={self.attachment.name}, complaint_id={self.complaint.id}>"
        )
