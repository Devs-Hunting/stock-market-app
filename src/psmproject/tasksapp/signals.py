from django.conf import settings
from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.urls import reverse
from fieldsignals import post_save_changed
from tasksapp.models import Offer, Task

from .tasks import send_mail_task
from .utils import receiver_not_in_test


def create_groups(sender, **kwargs):
    for group in settings.GROUP_NAMES:
        Group.objects.get_or_create(name=settings.GROUP_NAMES.get(group))


def build_absolute_url(path):
    return f"{settings.HOST_NAME}{path}"


@receiver_not_in_test(post_save_changed, sender=Task, fields=["selected_offer"])
def send_mail_offer_selected(sender, instance, **kwargs):
    if instance.selected_offer:
        create_solution_url = build_absolute_url(
            reverse("solution-create", kwargs={"offer_pk": instance.selected_offer.pk})
        )
        task_details_url = build_absolute_url(reverse("task-contractor-detail", kwargs={"pk": instance.pk}))
        message = (
            f"Dear contractor. We are glad to inform your that your offer for the task {instance.title} "
            f"has been accepted. Task details available under {task_details_url}. "
            f"You can upload your solution here {create_solution_url}."
        )
        contractor = instance.selected_offer.contractor

        send_mail_task.delay(subject="Offer accepted", message=message, recipient=contractor.email)


@receiver_not_in_test(post_save, sender=Offer)
def send_mail_offer_submitted(sender, instance, created, **kwargs):
    if created:
        offers_list_url = build_absolute_url(reverse("task-offers-list", kwargs={"pk": instance.task.pk}))
        offer_url = build_absolute_url(reverse("offer-detail", kwargs={"pk": instance.pk}))
        message = (
            f"Dear client. We are glad to inform your that there is new offer for your task "
            f"{instance.task.title} Offer details available under {offer_url}. "
            f"All offers for this task: {offers_list_url}."
        )
        client = instance.task.client
        send_mail_task.delay(subject="Offer submitted", message=message, recipient=client.email)
