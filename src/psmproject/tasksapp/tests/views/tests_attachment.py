import os
import shutil

from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from factories.factories import TaskAttachmentFactory, TaskFactory, UserFactory
from tasksapp.models import ATTACHMENTS_PATH, TaskAttachment

client = Client()


class TestTaskAttachmentAddView(TestCase):
    """
    Test case for add task attachment view
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test.
        Here it prepares test user, task, task attachment.
        """
        self.user = UserFactory.create()
        self.test_task = TaskFactory.create(client=self.user)
        self.attachment = SimpleUploadedFile("test_file.txt", b"content of test file")
        self.client.login(username=self.user.username, password="secret")
        super().setUp()

    def tearDown(self) -> None:
        """
        Clean up method after each test case. Deletes all created attachments files.
        """
        file_path = os.path.join(ATTACHMENTS_PATH)
        shutil.rmtree(file_path, ignore_errors=True)

    def test_should_return_correct_status_code_and_when_request_is_sent(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a request is sent.
        """
        response = self.client.get(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk})
        )

        self.assertEqual(response.status_code, 200)

    def test_should_add_attachment_to_existing_task(self):
        """
        Test whether the task attachment is added to the task by the user owner of task.
        """
        response = self.client.post(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            data={
                "task": self.test_task.id,
                "attachment": self.attachment,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.test_task.refresh_from_db()
        new_task_attachment = TaskAttachment.objects.get(task=self.test_task)
        self.assertEqual(
            str(new_task_attachment.attachment),
            f"{ATTACHMENTS_PATH}tasks/{self.test_task.id}/{self.attachment}",
        )
        self.assertEqual(len(self.test_task.attachments.all()), 1)

    def test_should_block_when_add_attachment_to_existing_task_by_other_user(self):
        """
        Test checks that it is not possible for another user to add an attachment to the task.
        """
        self.user2 = UserFactory.create()
        self.client.login(username=self.user2, password="secret")
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            data={
                "task": self.test_task.id,
                "attachment": self.attachment,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.test_task.refresh_from_db()
        with self.assertRaises(TaskAttachment.DoesNotExist):
            TaskAttachment.objects.get(task=self.test_task)

    def test_should_redirect_to_proper_url_after_success(self):
        """
        Test whether that the view redirects to the correct URL after a successful add attachment.
        """
        response = self.client.post(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            data={
                "task": self.test_task.id,
                "attachment": self.attachment,
            },
            follow=True,
        )

        self.assertRedirects(
            response, reverse("task-detail", kwargs={"pk": self.test_task.id})
        )

    def test_should_return_non_context_when_no_user_is_log_in(self):
        """
        Test checks that the view correctly redirects to the login page when a non logged in user
        attempts to access the view.
        """
        self.client.logout()
        response = client.get(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            follow=True,
        )
        self.assertRedirects(
            response, f"/users/accounts/login/?next=/tasks/{self.test_task.id}"
        )

    def test_should_block_adding_more_then_ten_attachments(self):
        """
        Test checks that view blocks adding more then ten attachments
        """
        TaskAttachmentFactory.create_batch(10, task=self.test_task)
        self.client.post(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            data={
                "task": self.test_task.id,
                "attachment": self.attachment,
            },
        )
        self.assertEqual(len(self.test_task.attachments.all()), 10)


class TestTaskAttachmentDeleteView(TestCase):
    """
    Test case for delete task attachment view
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test.
        Here it prepares test user, task, task attachment.
        """
        self.user = UserFactory.create()
        self.test_task = TaskFactory.create(client=self.user)
        self.attachment = TaskAttachmentFactory.create(task=self.test_task)
        self.client.login(username=self.user.username, password="secret")
        super().setUp()

    def tearDown(self) -> None:
        """
        Clean up method after each test case. Deletes all created attachments files.
        """
        file_path = os.path.join(ATTACHMENTS_PATH)
        shutil.rmtree(file_path, ignore_errors=True)

    def test_should_block_unauthorized_task_delete_access(self):
        """
        Test check if it is possible for another user to delete an attachment to the task.
        """
        self.other_task = TaskFactory.create()
        self.other_attachment = TaskAttachmentFactory.create(task=self.other_task)

        response = self.client.post(
            reverse("task-attachment-delete", kwargs={"pk": self.other_attachment.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            TaskAttachment.objects.filter(id=self.other_attachment.id).exists()
        )

    def test_should_delete_task_attachment_by_task_creator(self):
        """
        Test case to check if task attachment is deleted by user - owner of task.
        """
        response = self.client.post(
            reverse("task-attachment-delete", kwargs={"pk": self.attachment.id})
        )

        self.assertEqual(response.status_code, 302)
        self.test_task.refresh_from_db()
        self.assertFalse(TaskAttachment.objects.filter(id=self.attachment.id).exists())

    def test_should_delete_task_attachment_by_moderator(self):
        """
        Test case to check if task attachment is deleted by moderator - user in group MODERATOR.
        """
        self.user_moderator = UserFactory.create()
        moderator_group = Group.objects.create(name="MODERATOR")
        self.user_moderator.groups.add(moderator_group)
        self.client.login(username=self.user_moderator.username, password="secret")

        response = self.client.post(
            reverse("task-attachment-delete", kwargs={"pk": self.attachment.id})
        )
        self.assertEqual(response.status_code, 302)
        self.test_task.refresh_from_db()
        self.assertFalse(TaskAttachment.objects.filter(id=self.attachment.id).exists())

    def test_should_handle_attempt_to_delete_nonexistent_task_attachment(self):
        """
        Test case to check if attempt to delete non existent task attachment raises 404 error.
        """
        temp_attachment = TaskAttachmentFactory.create(task=self.test_task)
        temp_attachment_id = temp_attachment.id
        temp_attachment.delete()

        response = self.client.post(
            reverse("task-attachment-delete", kwargs={"pk": temp_attachment_id})
        )
        self.assertEqual(response.status_code, 404)


class TestTaskDownloadMethod(TransactionTestCase):
    """
    Test case for download task attachment view
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test.
        Here it prepares test user, task, task attachment.
        """
        self.user = UserFactory.create()
        self.test_task = TaskFactory.create(client=self.user)
        self.attachment = SimpleUploadedFile("test_file.txt", b"content of test file")
        self.test_taskattachment = TaskAttachment.objects.create(
            task=self.test_task, attachment=self.attachment
        )
        self.client.login(username=self.user.username, password="secret")
        super().setUp()

    def tearDown(self) -> None:
        """
        Clean up method after each test case. Deletes all created attachments files.
        """
        file_path = os.path.join(ATTACHMENTS_PATH)
        shutil.rmtree(file_path, ignore_errors=True)

    def test_should_download_attachment_from_task(self):
        """
        Test checks that correct attachment is downloaded.
        """
        response = self.client.get(
            reverse(
                "task-attachment-download", kwargs={"pk": self.test_taskattachment.id}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get("Content-Disposition"),
            f'attachment; filename="{self.test_taskattachment.attachment}"',
        )

    def test_should_handle_attempt_to_download_nonexistent_task_attachment(self):
        """
        Test case to check if attempt to download non existent task attachment raises 404 error.
        """
        temp_attachment = TaskAttachmentFactory.create(task=self.test_task)
        temp_attachment_id = temp_attachment.id
        temp_attachment.delete()

        response = self.client.post(
            reverse("task-attachment-download", kwargs={"pk": temp_attachment_id})
        )
        self.assertEqual(response.status_code, 404)
