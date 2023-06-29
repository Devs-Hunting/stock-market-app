import os
import shutil

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from tasksapp.models import Task, TaskAttachment

client = Client()


class TestTaskModel(TestCase):
    def setUp(self) -> None:
        super().setUp()

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_user = User.objects.create(username="test@test.pl", password="secret")
        cls.test_task = Task.objects.create(
            title="Test title",
            description="Test description",
            realization_time="2023-12-01",
            budget=1200.1200,
            client=cls.test_user,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()

    def test_should_return_max_length_for_title_field(self):
        """
        Test that check max length of title field.
        """
        task = Task.objects.get(id=1)
        max_length = task._meta.get_field("title").max_length
        self.assertEqual(max_length, 120)

    def test_should_return_correct_number_for_budget_field(self):
        """
        Test check that budget field is decimal number.
        """
        expected_number = "1200.12"
        task = Task.objects.get(id=1)
        actual_number = str(task.budget)

        self.assertEqual(expected_number, actual_number)

    def test_should_return_default_status_field_as_status_of_task_is_open(self):
        """
        Test check that status field has his default value = 0.
        """
        expected_status = 0
        task = Task.objects.get(id=1)
        actual_status = task.status

        self.assertEqual(expected_status, actual_status)

    def test_should_return_correct_text_as_represenation_of_object(self):
        """
        Test check that the representation of object Task has correct text.
        """
        expected_represenation = "<Task id=1, title=Test title>"
        task = Task.objects.get(id=1)
        actual_representation = repr(task)

        self.assertEqual(expected_represenation, actual_representation)

    def test_should_return_correct_string_representation(self):
        """
        Test check that the string representation of instance of object Task has correct text.
        """
        expected_string = "Task: Test title"
        task = Task.objects.get(id=1)
        actual_string = str(task)

        self.assertEqual(expected_string, actual_string)


class TestTaskAttachmentModel(TestCase):
    def setUp(self) -> None:
        super().setUp()

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.test_user2 = User.objects.create(
            username="test2@test.pl", password="secret"
        )
        cls.test_task = Task.objects.create(
            title="Test title",
            description="Test description",
            realization_time="2023-12-01",
            budget=1200.12,
            client=cls.test_user2,
        )
        cls.test_task_attachment = TaskAttachment.objects.create(
            task=cls.test_task,
            attachment=SimpleUploadedFile("test_file.txt", b"content of test file"),
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        file_path = os.path.join("attachments/tasks/1/")
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
        self.test_task_attachment = TaskAttachment(
            task=self.test_task,
            attachment=SimpleUploadedFile("test_file.txt", b"content of test file"),
        )
        self.test_task_attachment.save()

        with self.assertRaises(TaskAttachment.DoesNotExist):
            TaskAttachment.objects.get(id=1)

        new_attachment = TaskAttachment.objects.get(
            attachment=self.test_task_attachment.attachment.name
        )
        self.assertIsNotNone(new_attachment)

    def test_should_get_correct_upload_path_for_attachment_file(self):
        """
        Test checks that attachment files are uploaded on the right path.
        """
        expected_upload_path = "attachments/tasks/1/test_file.txt"
        task_attachment = TaskAttachment.objects.get(id=1)
        actual_upload_path = task_attachment.attachment

        self.assertEqual(expected_upload_path, actual_upload_path)

    def test_should_return_correct_text_as_represenation_of_object(self):
        """
        Test check that the string representation of instance of object Task has correct text.
        """
        expected_represenation = "<TaskAttachment id=1, attachment=attachments/tasks/1/test_file.txt, task_id=1>"
        task_attachment = TaskAttachment.objects.get(id=1)
        actual_representation = repr(task_attachment)

        self.assertEqual(expected_represenation, actual_representation)

    def test_should_return_correct_string_representation(self):
        """
        Test check that the string representation of instance of object Task has correct text.
        """
        expected_string = (
            "Attachment: attachments/tasks/1/test_file.txt for Task: Test title"
        )
        task_attachment = TaskAttachment.objects.get(id=1)
        actual_string = str(task_attachment)

        self.assertEqual(expected_string, actual_string)
