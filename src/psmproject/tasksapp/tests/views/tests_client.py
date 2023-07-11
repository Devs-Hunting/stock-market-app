from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from tasksapp.models import Task

client = Client()


class TestTaskListBaseView(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username="test1", password="secret")
        self.response = self.client.get(reverse("tasks-client-list"))

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
            description="New Test description2",
            realization_time="2023-12-31",
            budget=1000.12,
            client=cls.test_user1,
        )

    def test_should_return_status_code_200_when_request_by_name(self):

        self.assertEqual(self.response.status_code, 200)

    def test_should_check_that_view_use_correct_template(self):

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/tasks_list.html")

    def test_should_return_correct_context_when_request_is_sent(self):
        pass  # no contex in view

    def test_should_return_correct_objects_when_request_is_sent(self):

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/tasks_list.html")
        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_task2, self.test_task1],
        )

    def test_should_redirect_if_not_logged_in(self):
        self.client.logout()
        self.response = self.client.get(reverse("tasks-client-list"))
        self.assertRedirects(
            self.response, "accounts/"
        )  # check with allauth documentation

    def test_elements_should_be_sorted_by_id_from_newest(self):
        pass

    def test_should_return_objects_filtered_by_phrase_in_task_title(self):
        filter_word = "Second"
        response_filter = self.client.get(
            reverse("tasks-client-list"), QUERY_STRING=f"q={filter_word}"
        )
        self.assertEqual(
            list(response_filter.context["object_list"])[0], self.test_task2
        )
        self.assertEqual(len(response_filter.context["object_list"]), 1)

    def test_should_return_objects_filterd_by_phrases_in_task_description(self):
        filter_word = "New"
        response_filter = self.client.get(
            reverse("tasks-client-list"), QUERY_STRING=f"q={filter_word}"
        )
        self.assertEqual(
            list(response_filter.context["object_list"])[0], self.test_task2
        )
        self.assertEqual(len(response_filter.context["object_list"]), 1)


class TestTasksCurrentListView(TestCase):
    pass

    def test_should_return_only_active_task(self):
        pass


class TestTasksHistoricalListView(TestCase):
    pass

    def test_should_return_only_task_with_status_completed_and_cancelld(self):
        pass


class TestTaskCreateView(TestCase):
    pass
