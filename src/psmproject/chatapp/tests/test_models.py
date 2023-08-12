from chatapp.models import Chat, Message, Participant
from django.db.utils import IntegrityError
from django.test import TestCase
from factories.factories import (
    ChatFactory,
    ChatParticipantFactory,
    MessageFactory,
    RoleChoices,
    TaskChatFactory,
    TaskChatParticipantFactory,
    TaskFactory,
    UserFactory,
)


class TestChatModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_task = TaskFactory()
        cls.test_task_chat = TaskChatFactory(content_object=cls.test_task)
        cls.test_private_chat = ChatFactory()

    def test_should_assert_created_task_chat_exists_in_database(self):
        """
        Test if created task chat instance exists in database
        """
        self.assertTrue(Chat.objects.filter(id=self.test_task_chat.id).exists())

    def test_should_return_correct_content_object_is_linked_to_task_chat(self):
        """
        Test if task related chat instance is returning the correct assigned task
        """
        self.assertEqual(self.test_task_chat.content_object, self.test_task)

    def test_should_assert_created_private_chat_exists_in_database(self):
        """
        Test if created private chat instance exists in database
        """
        self.assertTrue(Chat.objects.filter(id=self.test_private_chat.id).exists())

    def test_should_return_correct_string_representation_of_created_chat(self):
        """
        Test if chat instance return correct string representation
        """
        expected = f"Chat - {self.test_private_chat.id}"
        self.assertEqual(str(self.test_private_chat), expected)


class TestParticipantModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_task = TaskFactory()
        cls.test_task_chat = TaskChatFactory()
        cls.test_private_chat = ChatFactory()
        cls.test_client = TaskChatParticipantFactory(
            chat=cls.test_task_chat,
            role=RoleChoices.CLIENT,
        )
        cls.test_contractor = TaskChatParticipantFactory(
            chat=cls.test_task_chat,
            role=RoleChoices.CONTRACTOR,
        )
        cls.test_arbiter = TaskChatParticipantFactory(
            chat=cls.test_task_chat,
            role=RoleChoices.ARBITER,
        )
        cls.test_moderator = TaskChatParticipantFactory(
            chat=cls.test_task_chat,
            role=RoleChoices.MODERATOR,
        )
        cls.test_participant1 = ChatParticipantFactory(chat=cls.test_private_chat)
        cls.test_participant2 = ChatParticipantFactory(chat=cls.test_private_chat)

    def test_should_assert_created_participant_exists_in_database_with_correct_role(self):
        """
        Test if created participant instance with role exists in database and return correct assigned role
        """
        self.assertTrue(Participant.objects.filter(id=self.test_client.id).exists())
        self.assertEqual(self.test_client.role, RoleChoices.CLIENT)

    def test_should_assert_created_participant_exists_in_database_without_assigned_role(self):
        """
        Test if created participant instance without role exists in database and has no assigned role
        """
        self.assertTrue(Participant.objects.filter(id=self.test_participant1.id).exists())
        self.assertIsNone(self.test_participant1.role)

    def test_should_throw_error_when_adding_participant_with_unknown_role(self):
        """
        Test if creating a participant instance with a role that does not exist in choices throws an error
        Testing constraint on role validation
        """
        with self.assertRaises(IntegrityError):
            ChatParticipantFactory(role="MT")

    def test_should_throw_error_when_adding_participant_that_already_exists_in_chat(self):
        """
        Test if creating twice a participant instance with same user and chat throws an error
        Testing constraint to avoid duplication of users in chat
        """
        new_chat = ChatFactory()
        new_user = UserFactory()
        with self.assertRaises(IntegrityError):
            ChatParticipantFactory(user=new_user, chat=new_chat)
            ChatParticipantFactory(user=new_user, chat=new_chat)

    def test_should_return_correct_number_of_participants_of_given_chat(self):
        """
        Test if chat participants return the correct number
        """
        actual_nb_of_participants = len(self.test_task_chat.participants.all())
        self.assertEqual(actual_nb_of_participants, 4)

    def test_should_assert_all_participants_are_deleted_following_related_chat_deletion(self):
        """
        Check if chat deletion cascade also to its participants
        """
        new_chat = ChatFactory()
        new_chat_participants = [ChatParticipantFactory(chat=new_chat) for i in range(2)]
        new_chat.delete()
        for participant in new_chat_participants:
            self.assertFalse(Participant.objects.filter(id=participant.id).exists())

    def test_should_return_correct_string_representation_of_created_participant_with_role(self):
        """
        Test if participant instance with role return correct string representation
        """
        expected = (
            f"{self.test_contractor.user.username} ({RoleChoices.CONTRACTOR.label}) "
            f"in Chat {self.test_contractor.chat.id}"
        )
        self.assertEqual(str(self.test_contractor), expected)

    def test_should_return_correct_string_representation_of_created_participant_without_role(self):
        """
        Test if participant instance without role return correct string representation
        """
        expected = f"{self.test_participant1.user.username} in Chat {self.test_participant1.chat.id}"
        self.assertEqual(str(self.test_participant1), expected)


class TestMessageModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_chat = ChatFactory()
        cls.test_user1 = UserFactory()
        cls.test_user2 = UserFactory()
        cls.test_message1 = MessageFactory(chat=cls.test_chat, author=cls.test_user1)
        cls.test_message2 = MessageFactory(chat=cls.test_chat, author=cls.test_user1)
        cls.test_message3 = MessageFactory(chat=cls.test_chat, author=cls.test_user2)

    def test_should_assert_created_message_exists_in_database(self):
        """
        Check if created message instance exists in database
        """
        self.assertTrue(Message.objects.filter(id=self.test_message1.id).exists())

    def test_should_return_correct_number_of_messages_in_given_chat(self):
        """
        Test if chat messages return the correct number
        """
        actual_nb_of_messages = len(self.test_chat.messages.all())
        self.assertEqual(actual_nb_of_messages, 3)

    def test_should_return_true_when_chat_deletion_also_delete_its_messages(self):
        """
        Check if chat deletion cascade also to related messages
        """
        new_chat = ChatFactory()
        new_chat_messages = [MessageFactory(chat=new_chat) for i in range(2)]
        new_chat.delete()
        for message in new_chat_messages:
            self.assertFalse(Message.objects.filter(id=message.id).exists())

    def test_should_return_correct_string_representation_of_created_message(self):
        """
        Test if message instance return correct string representation
        """
        expected = (
            f"{self.test_message1.timestamp.strftime('%Y-%m-%d %H:%M')}{self.test_message1.author}: "
            f"{self.test_message1.content}"
        )
        self.assertEqual(str(self.test_message1), expected)
