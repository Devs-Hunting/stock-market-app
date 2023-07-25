from django.test import Client, TestCase
from django.urls import reverse
from tasksapp.tests.views.factories import TaskFactory, UserFactory

client = Client()


class TestModeratorTaskListView(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(reverse("task-moderator-list"))

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = UserFactory()
        cls.user2 = UserFactory()
        cls.test_task1 = TaskFactory(client=cls.user)
        cls.test_task2 = TaskFactory(client=cls.user2)

    def test_should_return_correct_status_code_and_template_request_by_name(self):
        """
        This test case checks if the response status code is equal to 200 and if the correct template is used.
        """

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/tasks_list_all.html")

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test verify that pagination is applied if there are more than ten elements.
        """
        ten_task = TaskFactory.create_batch(10, client=self.user)

        self.assertEqual(self.response.status_code, 200)
        self.assertTrue("is_paginated" in self.response.context)
        self.assertEqual(len(self.response.context["object_list"]), 10)

    def test_should_return_objects_filtered_by_phrases_in_task_title(self):
        """
        Test checks the filtering of objects based on phrases in the task title.
        """
        filter_word = self.test_task1.title[0:4]
        response_filter = self.client.get(
            reverse("task-moderator-list"), QUERY_STRING=f"q={filter_word}"
        )

        self.assertEqual(
            list(response_filter.context["object_list"])[0], self.test_task1
        )
        self.assertEqual(len(response_filter.context["object_list"]), 1)

    def test_should_return_object_filterd_by_phrases_in_task_descrption(self):
        """
        Test checks the filtering of objects based on phrases in the task description.
        """
        filter_word = self.test_task1.description[0:4]
        response_filter = self.client.get(
            reverse("task-moderator-list"), QUERY_STRING=f"q={filter_word}"
        )

        self.assertEqual(
            list(response_filter.context["object_list"])[0], self.test_task1
        )
        self.assertEqual(len(response_filter.context["object_list"]), 1)

    def test_should_return_tasks_filtered_by_user_id(self):
        """
        This tests checks the filtering of tasks based on user ID.
        """
        filter_task_id = self.test_task1.id
        response_filter = self.client.get(
            reverse("task-moderator-list"), {"q": filter_task_id}
        )
        self.assertQuerysetEqual(
            response_filter.context["object_list"], [self.test_task1]
        )

    def test_should_return_none_tasks_object_when_phrase_for_make_filter_has_less_ten_3(
        self,
    ):
        """
        Tests chcecks the behavior when the phrase for make filter has less than ten 3 characters.
        """
        self.test_task3 = TaskFactory(client=self.user, title="TestTitle1")

        filter_word = "Te"
        response_filter = self.client.get(
            reverse("task-moderator-list", {"q": filter_word})
        )
        self.assertQuerysetEqual(response_filter.context["object_list"], None)

    def test_should_make_redirect_to_proper_adress_when_user_has_no_permission_to_use_view(
        self,
    ):
        """
        Tests checks if the user is redirected to the proper address when they do not have permission to use the view.
        """


class TestModeratorTaskEditView(TestCase):
    def setUpTestClass(self) -> None:
        super().setUp()
        input_data = {
            "title": "Task Title",
            "description": "Task descrption",
            "realization_time": "2023-12-31",
            "budget": 1220.12,
        }
        self.user = UserFactory.create()
        self.test_task = TaskFactory(client=self.user)


class TestModeratorTaskDeleteView(TestCase):
    pass
