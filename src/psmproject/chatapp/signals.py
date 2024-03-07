from chatapp.models import Chat, Participant, RoleChoices
from django.dispatch import receiver
from fieldsignals import post_save_changed
from tasksapp.models import Complaint, Task


@receiver(post_save_changed, sender=Task, fields=["selected_offer"])
def create_task_related_chat(sender, instance, **kwargs):
    if instance.selected_offer:
        chat = Chat.objects.create(content_object=instance)
        Participant.objects.create(user=instance.client, chat=chat, role=RoleChoices.CLIENT)
        Participant.objects.create(user=instance.selected_offer.contractor, chat=chat, role=RoleChoices.CONTRACTOR)


@receiver(post_save_changed, sender=Complaint, fields=["arbiter"])
def create_complaint_related_chat(sender, instance, **kwargs):
    if instance.arbiter:
        chat = Chat.objects.create(content_object=instance)
        Participant.objects.create(user=instance.task.client, chat=chat, role=RoleChoices.CLIENT)
        Participant.objects.create(user=instance.task.selected_offer.contractor, chat=chat, role=RoleChoices.CONTRACTOR)
        Participant.objects.create(user=instance.arbiter, chat=chat, role=RoleChoices.ARBITER)
