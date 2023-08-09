from chatapp.models import Participant
from django.test import TestCase
from factories.factories import ChatFactory, TaskChatFactory, TaskFactory, UserFactory


class TestParticipantModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_task = TaskFactory()
        cls.test_task_chat = TaskChatFactory()
        cls.test_private_chat = ChatFactory()
        cls.test_client = Participant.objects.create(
            user=UserFactory(),
            chat=cls.test_task_chat,
            role=Participant.RoleChoices.CLIENT,
        )
        cls.test_contractor = Participant.objects.create(
            user=UserFactory(),
            chat=cls.test_task_chat,
            role=Participant.RoleChoices.CONTRACTOR,
        )
        cls.test_arbiter = Participant.objects.create(
            user=UserFactory(),
            chat=cls.test_task_chat,
            role=Participant.RoleChoices.ARBITER,
        )
        cls.test_moderator = Participant.objects.create(
            user=UserFactory(),
            chat=cls.test_task_chat,
            role=Participant.RoleChoices.MODERATOR,
        )
        cls.test_participant1 = Participant.objects.create(user=UserFactory(), chat=cls.test_private_chat)
        cls.test_participant2 = Participant.objects.create(user=UserFactory(), chat=cls.test_private_chat)

    def test_should_return_true_when_task_related_participant_instance_created_in_database_with_role(
        self,
    ):
        participants = Participant.objects.all()
        self.assertIn(self.test_client, participants)
        self.assertEqual(self.test_client.role, Participant.RoleChoices.CLIENT)

    def test_should_return_true_when_private_chat_participant_instance_created_in_database_without_role(
        self,
    ):
        participants = Participant.objects.all()
        self.assertIn(self.test_participant1, participants)
        self.assertEqual(self.test_participant1.role, "")

    def test_should_return_right_number_of_participants_of_chat(self):
        actual_nb_of_participants = len(self.test_task_chat.participants.all())
        self.assertEqual(actual_nb_of_participants, 4)
