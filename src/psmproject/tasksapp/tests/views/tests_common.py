from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from tasksapp.models import Task

client = Client()


class TestTaskDetailView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.test_user1 = User.objects.create_user(
            username="test1", email="test1@test1.pl", password="secret"
        )

        cls.test_task1 = Task.objects.create(
            title="Test title",
            description="Test description",
            realization_time="2023-12-01",
            budget=1200.12,
            client=cls.test_user1,
        )
        cls.test_task2 = Task.objects.create(
            title="Second title",
            description="Test description2",
            realization_time="2023-12-31",
            budget=1000.12,
            client=cls.test_user1,
        )

    def test_should_return_status_code_200_when_request_by_name(self):
        self.client.login(username="test1", password="secret")
        self.response = self.client.get(
            reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )

        self.assertEqual(self.response.status_code, 200)

    def test_should_check_that_views_use_correct_template(self):
        self.client.login(username="test1", password="secret")
        self.response = self.client.get(
            reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/task_detail.html")

    def test_should_return_correct_context_when_request_is_sent(self):
        self.client.login(username="test1", password="secret")
        self.response = self.client.get(
            reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )
        # self.assertIn("attachments", self.response.context) add TaskAttachment object relateted to test_task1
        self.assertIn("task", self.response.context)

    """
    def test_should_return_correct_objects_when_request_is_sent(self):

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/tasks_list.html")
        self.assertEqual(list(self.response.context["object_list"]),[self.test_task2, self.test_task1])
        """

    def test_should_redirect_if_not_logged_in(self):
        self.client.logout()
        self.response = self.client.get(
            reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )
        self.assertRedirects(
            self.response, "accounts/"
        )  # check with allauth documentation


class TestTaskDeleteView(TestCase):
    pass
