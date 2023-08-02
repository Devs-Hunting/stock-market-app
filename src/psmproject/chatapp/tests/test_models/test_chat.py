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

    def testShouldReturnTrueWhenTaskChatInstanceCreatedInDatabase(self):
        chats = Chat.objects.all()
        self.assertIn(self.test_task_chat, chats)

    def testShouldReturnTrueWhenTaskIsProperlyLinkedWithCreatedTaskChat(self):
        self.assertEqual(self.test_task_chat.content_object, self.test_task)

    def testShouldReturnTrueWhenPrivateChatInstanceCreatedInDatabase(self):
        chats = Chat.objects.all()
        self.assertIn(self.test_private_chat, chats)
