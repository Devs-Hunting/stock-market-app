from django.test import Client, TestCase
from django.urls import reverse
from tasksapp.tests.views.factories import (
    TaskAttachmentFactory,
    TaskFactory,
    UserFactory,
)

client = Client()


class TestCommonTaskDetailView(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        super().setUpClass()

        cls.user = UserFactory()
        cls.test_task1 = TaskFactory(client=cls.user)
        cls.test_task2 = TaskFactory(client=cls.user)
        cls.test_attachment1 = TaskAttachmentFactory(task=cls.test_task1)
        cls.test_attachment2 = TaskAttachmentFactory(task=cls.test_task2)

    def test_should_return_status_code_200_when_request_by_name(self):
        self.client.login(username=self.user.username, password="secret")
        response = self.client.get(
            reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )

        self.assertEqual(response.status_code, 200)

    def test_should_check_that_views_use_correct_template(self):
        self.client.login(username=self.user.username, password="secret")
        response = self.client.get(
            reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasksapp/task_detail.html")

    def test_should_return_correct_context_when_request_is_sent(self):
        self.client.login(username=self.user.username, password="secret")
        response = self.client.get(
            reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )
        self.assertIn("attachments", response.context)
        self.assertIn("task", response.context)

    def test_should_return_correct_objects_when_request_is_sent(self):
        self.client.login(username=self.user.username, password="secret")
        response = self.client.get(
            reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasksapp/task_detail.html")
        self.assertEqual(response.context["task"], self.test_task1)

    def test_should_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(
            reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )
        self.assertRedirects(
            response, f"/users/accounts/login/?next=/tasks/{self.test_task1.id}"
        )


class TestCommonTaskDeleteView(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password="secret")

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = UserFactory()
        cls.user2 = UserFactory()
        cls.test_task1 = TaskFactory(client=cls.user)
        cls.test_task2 = TaskFactory(client=cls.user)
        cls.test_task3 = TaskFactory(client=cls.user)
        cls.test_attachment1 = TaskAttachmentFactory(task=cls.test_task1)
        cls.test_attachment2 = TaskAttachmentFactory(task=cls.test_task2)

    def test_should_return_status_code_200_when_request_by_name(self):
        response = self.client.get(
            reverse("task-delete", kwargs={"pk": self.test_task1.id})
        )

        self.assertEqual(response.status_code, 200)

    def test_should_check_that_views_use_correct_template(self):
        response = self.client.get(
            reverse("task-delete", kwargs={"pk": self.test_task1.id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasksapp/task_confirm_delete.html")

    def test_should_delete_task_as_client_that_is_creator_of_task(self):
        response = self.client.post(
            reverse("task-delete", kwargs={"pk": self.test_task1.id}), follow=True
        )

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.test_task1)
        self.assertRedirects(response, reverse("tasks-client-list"))

    def test_should_delete_task_as_moderator(self):
        pass  # should be tested after implementation of gropus for users

    def test_sholud_block_user_acces_if_is_not_creator_of_task(self):
        client.logout()
        client.login(username=self.user2.username, password="secret")
        response = self.client.post(
            reverse("task-delete", kwargs={"pk": self.test_task2.id}), follow=True
        )

        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(self.test_task2)

    def test_should_delete_task_if_it_has_status_canceled(self):
        self.test_task3.status = 5
        self.test_task3.save()
        self.test_task3.refresh_from_db()
        response = self.client.post(
            reverse("task-delete", kwargs={"pk": self.test_task3.id}), follow=True
        )

        self.assertEqual(response.status_code, 302)
        self.assertIsNone(self.test_task3)
        self.assertRedirects(response, reverse("tasks-client-list"))
