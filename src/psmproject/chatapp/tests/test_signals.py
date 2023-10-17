from chatapp.models import Chat, RoleChoices
from django.test import TestCase
from factories.factories import OfferFactory


class CreateTaskChatSignalTest(TestCase):
    def setUp(self):
        super().setUp()
        self.offer = OfferFactory()
        self.task = self.offer.task

    def test_should_confirm_task_chat_creation_with_correct_participants_when_offer_is_selected(self):
        """
        Checking if chat is created when selecting an offer for a task,
        it should return the correct users with the correct roles
        """
        self.task.selected_offer = self.offer
        self.task.save(update_fields=["selected_offer"])
        chat = Chat.objects.get(object_id=self.task.id)
        participants = chat.participants.all()
        self.assertTrue(Chat.objects.filter(pk=chat.pk).exists())
        self.assertEqual(participants.get(role=RoleChoices.CLIENT).user, self.task.client)
        self.assertEqual(participants.get(role=RoleChoices.CONTRACTOR).user, self.offer.contractor)

    def test_should_return_empty_queryset_when_offer_not_selected_for_task(self):
        """
        Checking if no chat instance exists when no offer has been selected so far
        """
        with self.assertRaises(Chat.DoesNotExist):
            Chat.objects.get(object_id=self.task.id)
