from chatapp.models import Chat, Message, Participant
from django.test import TestCase
from factories.factories import ChatFactory, TaskChatFactory, TaskFactory, UserFactory


class TestChatModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_task = TaskFactory()
        cls.test_task_chat = Chat.objects.create(content_object=cls.test_task)
        cls.test_private_chat = Chat.objects.create()

    def test_should_return_true_when_task_chat_instance_created_in_database(self):
        chats = Chat.objects.all()
        self.assertIn(self.test_task_chat, chats)

    def test_should_return_true_when_task_is_properly_linked_with_created_task_chat(self):
        self.assertEqual(self.test_task_chat.content_object, self.test_task)

    def test_should_return_true_when_private_chat_instance_created_in_database(self):
        chats = Chat.objects.all()
        self.assertIn(self.test_private_chat, chats)

    def test_should_return_correct_string_representation_of_created_chat_object(self):
        expected = f"Chat - {self.test_private_chat.id}"
        self.assertEqual(str(self.test_private_chat), expected)


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

    def test_should_return_correct_string_representation_of_created_participant_object_with_role(self):
        expected = (
            f"{self.test_contractor.user.username} ({Participant.RoleChoices.CONTRACTOR.label}) "
            f"in Chat {self.test_contractor.chat.id}"
        )
        self.assertEqual(str(self.test_contractor), expected)

    def test_should_return_correct_string_representation_of_created_participant_object_without_role(self):
        expected = f"{self.test_participant1.user.username} () in Chat {self.test_participant1.chat.id}"
        self.assertEqual(str(self.test_participant1), expected)


class TestMessageModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_chat = ChatFactory()
        cls.test_user1 = UserFactory()
        cls.test_user2 = UserFactory()
        cls.test_message1 = Message.objects.create(chat=cls.test_chat, author=cls.test_user1, content="message1")
        cls.test_message2 = Message.objects.create(chat=cls.test_chat, author=cls.test_user1, content="message2")
        cls.test_message3 = Message.objects.create(chat=cls.test_chat, author=cls.test_user2, content="message3")

    def test_should_return_true_when_message_instance_created_in_database(self):
        messages = Message.objects.all()
        self.assertIn(self.test_message1, messages)

    def test_should_return_right_number_of_messages_displayed_in_chat(self):
        actual_nb_of_messages = len(self.test_chat.messages.all())
        self.assertEqual(actual_nb_of_messages, 3)

    def test_should_return_correct_string_representation_of_created_message_object(self):
        expected = (
            f"{self.test_message1.timestamp.strftime('%Y-%m-%d %H:%M')}{self.test_message1.author}: "
            f"{self.test_message1.content}"
        )
        self.assertEqual(str(self.test_message1), expected)
