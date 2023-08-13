import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from tasksapp.models import Task


class Offer(models.Model):
    """
    This model represents a Offer. Is related to Task (as offer and selected offer), Solution and Contractor.
    It includes information such as: description, expected realization time, budget, created_at.
    Offer could be accepted then it will be selected offer.
    If the offer is accepted then will be made a solution for it and
    when the solution is accepted then the offer should be paid.
    """

    description = models.TextField()
    # solution = models.OneToOneField(Solution, related_name="offer", null=True, on_delete=models.SET_NULL)
    task = models.ForeignKey(Task, related_name="task", null=True, on_delete=models.CASCADE)
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
