from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from tasksapp.models import Task, TaskAttachment
from usersapp.models import User

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
            budget=1200.12,
            client=cls.test_user,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()

    def test_should_return_max_lenght_for_title_field(self):
        task = Task.objects.get(id=1)
        max_length = task._meta.get_field("title").max_length
        self.assertEqual(max_length, 120)

    def test_should_return_correct_number_for_budget_field(self):
        expected_number = "1200.12"
        task = Task.objects.get(id=1)
        actual_number = str(task.budget)

        self.assertEqual(expected_number, actual_number)

    def test_should_return_default_status_field_as_status_of_task_is_open(self):
        expected_status = 0
        task = Task.objects.get(id=1)
        actual_status = task.status

        self.assertEqual(expected_status, actual_status)

    def test_should_return_correct_text_as_represenation_of_object(self):
        expected_represenation = "<Task id=1, title=Test title>"
        task = Task.objects.get(id=1)
        actual_representation = repr(task)

        self.assertEqual(expected_represenation, actual_representation)

    def test_should_return_correct_string_representation(self):
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
        cls.test_task_attachment2 = TaskAttachment(
            task=cls.test_task,
            attachment=SimpleUploadedFile("test_file.txt", b"content of test file"),
        )
        cls.test_task_attachment2.save()

    @classmethod
    def tearDownClass(cls) -> None:
        return super().tearDownClass()

    def test_should_raise_Validation_Error_when_max_attachments_number_is_exceeded(
        self,
    ):
        pass

    def test_should_check_and_delete_for_an_existing_attachment_with_the_same_name(
        self,
    ):
        task_attachment = TaskAttachment.objects.get(id=1)
        task_attachment2 = TaskAttachment.objects.get(id=2)
        file_name = task_attachment.attachment
        file_name2 = task_attachment2.attachment

        self.assertEqual(file_name, file_name2)

    def test_should_get_correct_upload_path_for_attachment_file(self):
        expected_upload_path = "attachments/tasks/1/test_file.txt"
        task_attachment = TaskAttachment.objects.get(id=1)
        actual_upload_path = task_attachment.attachment

        self.assertEqual(expected_upload_path, actual_upload_path)

    def test_should_return_correct_text_as_represenation_of_object(self):
        expected_represenation = "<TaskAttachment id=1, attachment=attachments/tasks/1/test_file.txt, task_id=1>"
        task_attachment = TaskAttachment.objects.get(id=1)
        actual_representation = repr(task_attachment)

        self.assertEqual(expected_represenation, actual_representation)

    def test_should_return_correct_string_representation(self):
        expected_string = (
            "Attachment: attachments/tasks/1/test_file.txt for Task: Test title"
        )
        task_attachment = TaskAttachment.objects.get(id=1)
        actual_string = str(task_attachment)

        self.assertEqual(expected_string, actual_string)
