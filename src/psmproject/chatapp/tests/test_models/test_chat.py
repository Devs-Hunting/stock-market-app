from chatapp.models import Chat
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from tasksapp.models import Task


class TestChatModel(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_user = get_user_model().objects.create_user(
            username="test@test.pl", password="secret"
        )
        cls.test_task = Task.objects.create(
            title="Test title",
            description="Test description",
            realization_time="2023-12-01",
            budget=10.00,
            client=cls.test_user,
        )
        cls.test_task_content_type = ContentType.objects.get_for_model(cls.test_task)
        cls.test_task_chat = Chat.objects.create(
            content_type=cls.test_task_content_type, object_id=cls.test_task.id
        )
        cls.test_user_content_type = ContentType.objects.get_for_model(cls.test_user)
        cls.test_user_chat = Chat.objects.create(
            content_type=cls.test_user_content_type, object_id=cls.test_user.id
        )

    def testShouldReturnTrueWhenTaskChatInstanceCreatedInDatabase(self):
        chats = Chat.objects.all()
        self.assertIn(self.test_task_chat, chats)

    def testShouldReturnTrueWhenUserChatInstanceCreatedInDatabase(self):
        users = Chat.objects.all()
        self.assertIn(self.test_user_chat, users)
