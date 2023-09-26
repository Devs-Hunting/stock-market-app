from chatapp.models import Chat, Participant, RoleChoices
from django.dispatch import receiver
from fieldsignals import post_save_changed
from tasksapp.models import Task


@receiver(post_save_changed, sender=Task, fields=["selected_offer"])
def create_task_related_chat(sender, instance, **kwargs):
    if instance.selected_offer:
        chat = Chat.objects.create(content_object=instance)
        Participant.objects.create(user=instance.client, chat=chat, role=RoleChoices.CLIENT)
        Participant.objects.create(user=instance.selected_offer.contractor, chat=chat, role=RoleChoices.CONTRACTOR)
