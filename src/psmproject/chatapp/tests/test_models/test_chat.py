from chatapp.models import Chat
from django.test import TestCase
from factories.factories import TaskFactory


class TestChatModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_task = TaskFactory()
        cls.test_task_chat = Chat.objects.create(obj=cls.test_task)
        cls.test_private_chat = Chat.objects.create()

    def test_should_return_true_when_task_chat_instance_created_in_database(self):
        chats = Chat.objects.all()
        self.assertIn(self.test_task_chat, chats)

    def test_should_return_true_when_task_is_properly_linked_with_created_task_chat(self):
        self.assertEqual(self.test_task_chat.content_object, self.test_task)

    def test_should_return_true_when_private_chat_instance_created_in_database(self):
        chats = Chat.objects.all()
        self.assertIn(self.test_private_chat, chats)
