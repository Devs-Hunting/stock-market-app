import os
import shutil

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from tasksapp.models import Task, TaskAttachment


class TestTaskBase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_user = User.objects.create_user(
            username="test@test.pl", password="secret"
        )
        cls.test_task = Task.objects.create(
            title="Test title",
            description="Test description",
            realization_time="2023-12-01",
            budget=1200.1200,
            client=cls.test_user,
        )


class TestTaskModel(TestTaskBase):
    def test_should_return_max_length_for_title_field(self):
        """
        Test that check max length of title field.
        """
        max_length = self.test_task._meta.get_field("title").max_length

        self.assertEqual(max_length, 120)

    def test_should_return_correct_number_for_budget_field(self):
        """
        Test check that budget field is decimal number.
        """
        expected_number = "1200.12"
        actual_number = str(self.test_task.budget)

        self.assertEqual(expected_number, actual_number)

    def test_should_return_default_status_field_as_status_of_task_is_open(self):
        """
        Test check that status field has his default value = 0.
        """
        expected_status = 0
        actual_status = self.test_task.status

        self.assertEqual(expected_status, actual_status)

    def test_should_return_correct_text_as_represenation_of_object(self):
        """
        Test check that the representation of object Task has correct text.
        """
        expected_represenation = (
            f"<Task id={self.test_task.id}, title={self.test_task.title}>"
        )
        actual_representation = repr(self.test_task)

        self.assertEqual(expected_represenation, actual_representation)

    def test_should_return_correct_string_representation(self):
        """
        Test check that the string representation of instance of object Task has correct text.
        """
        expected_string = "Task: Test title"
        actual_string = str(self.test_task)

        self.assertEqual(expected_string, actual_string)


class TestTaskAttachmentModel(TestTaskBase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_task_attachment = TaskAttachment.objects.create(
            task=cls.test_task,
            attachment=SimpleUploadedFile("test_file.txt", b"content of test file"),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        file_path = os.path.dirname(
            os.path.dirname(os.path.dirname(cls.test_task_attachment.attachment.path))
        )
        shutil.rmtree(file_path, ignore_errors=True)

    def test_should_raise_Validation_Error_when_max_attachments_number_is_exceeded(
        self,
    ):
        """
        Test checks that when max number of attachments is exceeded is raised ValidationError.
        """
        for index in range(TaskAttachment.MAX_ATTACHMENTS):
            TaskAttachment.objects.create(
                task=self.test_task,
                attachment=SimpleUploadedFile(
                    f"test_file_{index}.txt", b"content of test file"
                ),
            )
        self.task_attachment = TaskAttachment.objects.create(
            task=self.test_task,
            attachment=SimpleUploadedFile("test_file.txt", b"content of test file"),
        )
        with self.assertRaises(ValidationError):
            self.task_attachment.clean()

    def test_should_check_and_delete_for_an_existing_attachment_with_the_same_name(
        self,
    ):
        """
        Test checks that overwrite method save() checks and delete an existing attachment with the same file name.
        """
        TaskAttachment.objects.create(
            task=self.test_task,
            attachment=SimpleUploadedFile("test_file.txt", b"content of test file"),
        )

        with self.assertRaises(TaskAttachment.DoesNotExist):
            TaskAttachment.objects.get(id=self.test_task_attachment.id)

        new_attachment_path = f"attachments/tasks/{self.test_task.id}/test_file.txt"
        new_attachment = TaskAttachment.objects.get(attachment=new_attachment_path)
        self.assertIsNotNone(new_attachment)

    def test_should_get_correct_upload_path_for_attachment_file(self):
        """
        Test checks that attachment files are uploaded on the right path.
        """
        expected_upload_path = f"attachments/tasks/{self.test_task.id}/test_file.txt"
        actual_upload_path = str(self.test_task_attachment.attachment)

        self.assertEqual(expected_upload_path, actual_upload_path)

    def test_should_return_correct_text_as_represenation_of_object(self):
        """
        Test check that the string representation of instance of object Task has correct text.
        """
        expected_represenation = (
            f"<TaskAttachment id={self.test_task_attachment.id}, "
            f"attachment={self.test_task_attachment.attachment}, task_id={self.test_task.id}>"
        )
        actual_representation = repr(self.test_task_attachment)

        self.assertEqual(expected_represenation, actual_representation)

    def test_should_return_correct_string_representation(self):
        """
        Test check that the string representation of instance of object Task has correct text.
        """
        expected_string = (
            f"Attachment: attachments/tasks/{self.test_task.id}/"
            f"test_file.txt for Task: {self.test_task.title}"
        )
        actual_string = str(self.test_task_attachment)

        self.assertEqual(expected_string, actual_string)
