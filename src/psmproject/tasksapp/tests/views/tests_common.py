import os
import shutil

from django.test import Client, TestCase
from django.urls import reverse
from factories.factories import TaskAttachmentFactory, TaskFactory, UserFactory
from tasksapp.models import ATTACHMENTS_PATH, Task


class TestCommonTaskDetailView(TestCase):
    """
    Test case for the Task Detail View
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase
        """
        super().setUpTestData()
        cls.user = UserFactory()
        cls.test_task1 = TaskFactory(client=cls.user)
        cls.test_task2 = TaskFactory(client=cls.user)
        cls.test_attachment1 = TaskAttachmentFactory(task=cls.test_task1)
        cls.test_attachment2 = TaskAttachmentFactory(task=cls.test_task2)

    def tearDown(self) -> None:
        file_path = os.path.join(ATTACHMENTS_PATH)
        shutil.rmtree(file_path, ignore_errors=True)

    def test_should_retrieve_task_detail_with_valid_task_id(self):
        """
        Test case to check if Task Detail View works correctly with a valid task id
        """
        self.client.login(username=self.user.username, password="secret")
        response = self.client.get(reverse("task-detail", kwargs={"pk": self.test_task1.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tasksapp/task_detail.html")
        self.assertIn("attachments", response.context)
        self.assertIn("task", response.context)
        self.assertEqual(response.context["task"], self.test_task1)

    def test_should_require_login_for_task_detail_access(self):
        """
        Test case to check if Task Detail View requires user login
        """
        self.client.logout()
        response = self.client.get(reverse("task-detail", kwargs={"pk": self.test_task1.id}))
        self.assertRedirects(response, f"/users/accounts/login/?next=/tasks/{self.test_task1.id}")


class TaskDeleteViewTest(TestCase):
    """
    Test case for the Task Delete View
    """

    def setUp(self):
        """
        Set up data for each individual test
        """
        self.client = Client()
        self.user = UserFactory.create()
        self.task = TaskFactory.create(client=self.user)
        self.client.force_login(self.user)

    def tearDown(self) -> None:
        file_path = os.path.join(ATTACHMENTS_PATH)
        shutil.rmtree(file_path, ignore_errors=True)

    def test_should_block_unauthorized_task_delete_access(self):
        """
        Test case to check if unauthorized task deletion is blocked
        """
        other_task = TaskFactory.create()

        response = self.client.get(reverse("task-delete", args=[other_task.id]))
        self.assertEqual(response.status_code, 302)

    def test_should_delete_task_with_allowed_statuses(self):
        """
        Test case to check if tasks with allowed statuses are deleted
        """
        for status in [Task.TaskStatus.OPEN, Task.TaskStatus.ON_HOLD]:
            self.task.status = status
            self.task.save()

            task_from_db = Task.objects.get(id=self.task.id)
            self.assertEqual(task_from_db.status, status)

            response = self.client.post(reverse("task-delete", args=[self.task.id]))
            self.assertEqual(response.status_code, 302)
            self.assertFalse(Task.objects.filter(id=self.task.id).exists())

            # Recreate the task for the next loop iteration
            self.task = TaskFactory.create(client=self.user)

    def test_should_not_delete_task_with_disallowed_statuses(self):
        """
        Test case to check if tasks with disallowed statuses are not deleted
        """
        for status in [
            Task.TaskStatus.ON_GOING,
            Task.TaskStatus.OBJECTIONS,
            Task.TaskStatus.COMPLETED,
            Task.TaskStatus.CANCELLED,
        ]:
            self.task.status = status
            self.task.save()

            task_from_db = Task.objects.get(id=self.task.id)
            self.assertEqual(task_from_db.status, status)

            response = self.client.post(reverse("task-delete", args=[self.task.id]))
            self.assertEqual(response.status_code, 302)
            self.assertTrue(Task.objects.filter(id=self.task.id).exists())

    def test_should_allow_creator_to_delete_task(self):
        """
        Test case to check if task creator can delete the task
        """
        response = self.client.post(reverse("task-delete", args=[self.task.id]))
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=self.task.id)

    def test_should_handle_attempt_to_delete_nonexistent_task(self):
        """
        Test case to check if attempting to delete a non-existent task is handled correctly
        """
        temp_task = TaskFactory.create(client=self.user)
        temp_task_id = temp_task.id
        temp_task.delete()

        response = self.client.post(reverse("task-delete", args=[temp_task_id]))
        self.assertEqual(response.status_code, 404)
