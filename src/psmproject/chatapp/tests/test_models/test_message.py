from chatapp.models import Message
from django.test import TestCase
from factories.factories import ChatFactory, UserFactory


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
