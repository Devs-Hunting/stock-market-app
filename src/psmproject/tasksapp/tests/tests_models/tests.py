from django.test import Client, TestCase
from tasksapp.models import Task
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
        pass

    def test_should_return_correct_number_for_budget_field(self):
        pass

    def test_should_return_default_status_field_as_open(self):
        pass

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
