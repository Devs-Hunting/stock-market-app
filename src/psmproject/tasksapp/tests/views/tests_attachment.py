import os
import shutil

from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from factories.factories import TaskAttachmentFactory, TaskFactory, UserFactory
from tasksapp.models import ATTACHMENTS_PATH, TaskAttachment


class TestTaskAttachmentAddView(TestCase):
    """
    Test case for add task attachment view
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test.
        Here it prepares test user, task, task attachment.
        """
        self.client = Client()
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
        response = self.client.get(reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}))

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

    def test_should_raise_exception_when_adding_attachment_to_non_existing_task(self):
        """
        Test checks that it is not possible to add an attachment to a non existing task.
        """
        # B should be error ObjectDoesNotExist - method get_task() - return None when exception - error in test_func()
        with self.assertRaises(ObjectDoesNotExist):
            self.client.post(
                reverse("task-add-attachment", kwargs={"pk": 999}),
                data={
                    "task": 999,
                    "attachment": self.attachment,
                },
                follow=True,
            )

    def test_should_block_when_add_attachment_to_existing_task_by_other_user(self):
        """
        Test checks that it is not possible for another user to add an attachment to the task.
        """
        self.user2 = UserFactory.create()
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

        self.assertRedirects(response, reverse("task-detail", kwargs={"pk": self.test_task.id}))

    def test_should_return_non_context_when_non_logged_in_user_is_trying_to_access(self):
        """
        Test checks that the view correctly redirects to the login page when a non logged in user
        attempts to access the view.
        """
        self.client.logout()
        response = self.client.get(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            follow=True,
        )
        self.assertRedirects(response, f"/users/accounts/login/?next=/tasks/{self.test_task.id}")

    def test_should_block_when_adding_more_than_ten_attachments(self):
        """
        Test checks that view blocks adding more then ten attachments
        """
        for i in range(10):
            self.attachment_new = SimpleUploadedFile(f"test_file_{i}.txt", b"content of test file")
            self.client.post(
                reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
                data={
                    "task": self.test_task.id,
                    "attachment": self.attachment_new,
                },
            )

        attachment_eleven = SimpleUploadedFile("test_file_11.txt", b"content of test file")
        self.client.post(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            data={
                "task": self.test_task.id,
                "attachment": attachment_eleven,
            },
        )
        self.assertEqual(len(self.test_task.attachments.all()), 10)

    def test_should_overwrite_attachment_with_same_name(self):
        """
        Test checks that attachment is overwritten when it has the same name
        """
        self.attachment_new = SimpleUploadedFile("test_file.txt", b"New content of test file")
        self.client.post(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            data={
                "task": self.test_task.id,
                "attachment": self.attachment,
            },
            follow=True,
        )
        self.client.post(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            data={
                "task": self.test_task.id,
                "attachment": self.attachment_new,
            },
            follow=True,
        )
        new_task_attachment = TaskAttachment.objects.get(task=self.test_task)
        file = new_task_attachment.attachment.open("r")
        file_content = file.read()
        self.assertEqual(file_content, "New content of test file")
        self.assertEqual(len(self.test_task.attachments.all()), 1)

    def test_should_raise_exception_when_adding_attachment_file_with_non_content(self):
        """
        Test checks that it is not possible to add attachment file with non content - empty file
        """
        empty_file = SimpleUploadedFile("empty_file.txt", b"", content_type="text/plain")
        response = self.client.post(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            data={
                "task": self.test_task.id,
                "attachment": empty_file,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(self.test_task.attachments.all()), 0)
        with self.assertRaises(ObjectDoesNotExist):
            TaskAttachment.objects.get(task=self.test_task)

    def test_should_block_adding_attachment_with_non_supported_content_type(self):
        """
        Test checks that is possible to add attachment with non supported content type
        """
        wrong_file = SimpleUploadedFile("test_file.jpg", b"content of test file", content_type="image/jpeg")
        response = self.client.post(
            reverse("task-add-attachment", kwargs={"pk": self.test_task.pk}),
            data={
                "task": self.test_task.id,
                "attachment": wrong_file,
            },
            follow=True,
        )
        self.assertEqual(len(self.test_task.attachments.all()), 0)
        self.assertContains(response, "File type is not supported")


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
        Test check if it is possible for another user to delete an attachment to the task
        and redirect to proper url.
        """
        self.other_task = TaskFactory.create()
        self.other_attachment = TaskAttachmentFactory.create(task=self.other_task)

        response = self.client.post(reverse("task-attachment-delete", kwargs={"pk": self.other_attachment.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task-detail", kwargs={"pk": self.other_task.pk}))
        self.assertTrue(TaskAttachment.objects.filter(id=self.other_attachment.id).exists())

    def test_should_delete_task_attachment_by_task_creator_and_redirect_to_proper_url(self):
        """
        Test case to check if task attachment is deleted by user - owner of task and redirect to proper url.
        """
        response = self.client.post(reverse("task-attachment-delete", kwargs={"pk": self.attachment.id}))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task-detail", kwargs={"pk": self.test_task.pk}))
        self.test_task.refresh_from_db()
        self.assertFalse(TaskAttachment.objects.filter(id=self.attachment.id).exists())

    def test_should_delete_task_attachment_by_moderator_and_redirects_to_proper_url(self):
        """
        Test case to check if task attachment is deleted by moderator - user in group MODERATOR.
        and redirect to proper url.
        """
        self.user_moderator = UserFactory.create()
        moderator_group = Group.objects.create(name="MODERATOR")
        self.user_moderator.groups.add(moderator_group)
        self.client.login(username=self.user_moderator.username, password="secret")

        response = self.client.post(reverse("task-attachment-delete", kwargs={"pk": self.attachment.id}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("task-detail", kwargs={"pk": self.test_task.pk}))
        self.test_task.refresh_from_db()
        self.assertFalse(TaskAttachment.objects.filter(id=self.attachment.id).exists())

    def test_should_handle_attempt_to_delete_nonexistent_task_attachment(self):
        """
        Test case to check if attempt to delete non existent task attachment raises 404 error.
        """
        temp_attachment = TaskAttachmentFactory.create(task=self.test_task)
        temp_attachment_id = temp_attachment.id
        temp_attachment.delete()

        response = self.client.post(reverse("task-attachment-delete", kwargs={"pk": temp_attachment_id}))
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
        self.test_taskattachment = TaskAttachment.objects.create(task=self.test_task, attachment=self.attachment)
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
        response = self.client.get(reverse("task-attachment-download", kwargs={"pk": self.test_taskattachment.id}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.get("Content-Disposition"),
            f'attachment; filename="{self.test_taskattachment.attachment}"',
        )

    def test_should_check_content_of_attachment_file_with_downloaded_file(self):
        """
        Test checks that downloaded file has correct content.
        """
        response = self.client.get(reverse("task-attachment-download", kwargs={"pk": self.test_taskattachment.id}))
        self.assertEqual(response.content, b"content of test file")

    def test_should_handle_attempt_to_download_nonexistent_task_attachment(self):
        """
        Test case to check if attempt to download non existent task attachment raises 404 error.
        """
        temp_attachment = TaskAttachmentFactory.create(task=self.test_task)
        temp_attachment_id = temp_attachment.id
        temp_attachment.delete()

        response = self.client.get(reverse("task-attachment-download", kwargs={"pk": temp_attachment_id}))
        self.assertEqual(response.status_code, 404)

    def test_should_handle_attempt_to_download_task_attachment_for_deleted_task(self):
        """
        Test check if attempt to download task attachment for deleted task raises 404 error.
        """
        self.test_task.delete()
        response = self.client.get(reverse("task-attachment-download", kwargs={"pk": self.test_taskattachment.id}))

        self.assertEqual(response.status_code, 404)
