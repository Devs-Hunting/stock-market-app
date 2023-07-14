from django.test import Client, TestCase
from django.urls import reverse
from tasksapp.models import Task
from tasksapp.tests.views.factories import TaskFactory, UserFactory

client = Client()


class TestClientTaskListBaseView(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(reverse("tasks-client-list"))

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = UserFactory()
        cls.test_task1 = TaskFactory(client=cls.user)
        cls.test_task2 = TaskFactory(client=cls.user)

    def test_should_return_status_code_200_when_request_by_name(self):

        self.assertEqual(self.response.status_code, 200)

    def test_should_check_that_view_use_correct_template(self):

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/tasks_list.html")

    def test_should_return_correct_objects_when_request_is_sent(self):

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/tasks_list.html")
        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_task2, self.test_task1],
        )

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        pass

    def test_should_redirect_if_not_logged_in(self):
        self.client.logout()
        self.response = self.client.get(reverse("tasks-client-list"))
        self.assertRedirects(self.response, f"/users/accounts/login/?next=/tasks/")

    def test_elements_should_be_sorted_by_id_from_newest(self):

        self.assertEqual(list(self.response.context["object_list"])[0], self.test_task2)

    def test_should_return_objects_filtered_by_phrase_in_task_title(self):
        filter_word = self.test_task2.title[0:4]
        response_filter = self.client.get(
            reverse("tasks-client-list"), QUERY_STRING=f"q={filter_word}"
        )
        self.assertEqual(
            list(response_filter.context["object_list"])[0], self.test_task2
        )
        self.assertEqual(len(response_filter.context["object_list"]), 1)

    def test_should_return_objects_filterd_by_phrases_in_task_description(self):
        filter_word = self.test_task2.description[0:4]
        response_filter = self.client.get(
            reverse("tasks-client-list"), QUERY_STRING=f"q={filter_word}"
        )
        self.assertEqual(
            list(response_filter.context["object_list"])[0], self.test_task2
        )
        self.assertEqual(len(response_filter.context["object_list"]), 1)


class TestClientTasksCurrentListView(TestClientTaskListBaseView):
    def test_should_return_only_active_task(self):
        tasks_list = [self.test_task2, self.test_task1]

        self.assertEqual(list(self.response.context["object_list"]), tasks_list)
        self.assertEqual(len(self.response.context["object_list"]), 2)


class TestClientTasksHistoricalListView(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(reverse("tasks-client-history-list"))

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = UserFactory()
        cls.test_task1 = TaskFactory(client=cls.user)
        cls.test_task2 = TaskFactory(client=cls.user)

    def test_should_check_that_view_use_correct_template(self):

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/tasks_history_list.html")

    def test_should_return_only_task_with_status_completed_and_cancelld(self):
        self.test_task2.status = 4
        self.test_task2.save()
        self.test_task2.refresh_from_db()

        self.assertEqual(list(self.response.context["object_list"]), self.test_task2)
        self.assertEqual(len(self.response.context["object_list"]), 1)


class TestClientTaskCreateView(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.client.force_login(self.user)
        self.data = {
            "title": "Task Title",
            "description": "Task descrption",
            "realization_time": "2023-12-31",
            "budget": 1220.12,
        }

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = UserFactory()

    def test_should_return_status_code_200_when_request_is_sent(self):
        response = client.get(reverse("task-create"))

        self.assertEqual(response.status_code, 200)

    def test_should_create_task_object(self):
        response = client.post(reverse("task-create"), data=self.data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.filter(title=self.data["title"]).count(), 1)

    def test_should_redirect_to_proper_url_after_success(self):
        response = client.post(reverse("task-create"), data=self.data, follow=True)

        self.assertRedirects(
            response,
            reverse("tasks-client-list"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_sholud_return_non_context_when_no_user_is_log_in(self):
        self.client.logout()
        response = client.get(reverse("task-create"))

        self.assertRedirects(response, "/users/accounts/login/?next=/tasks/add/")


class TestClientTaskEditView(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.client.force_login(self.user)
        self.data = {
            "title": "Task Title",
            "description": "Task descrption",
            "realization_time": "2023-12-31",
            "budget": 1220.12,
        }

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = UserFactory()
        cls.test_task1 = TaskFactory(client=cls.user)

    def test_should_return_status_code_302_when_request_is_sent(self):
        response = self.client.post(
            reverse("task-edit", kwargs={"pk": self.test_task1.id}),
            data=self.data,
        )

        self.assertEqual(response.status_code, 302)

    def test_should_update_existing_task_object(self):
        response = self.client.post(
            reverse("task-edit", kwargs={"pk": self.test_task1.id}),
            data=self.data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response, reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )
        self.test_task1.refresh_from_db()
        self.assertEqual(self.test_task1.title, self.data["title"])
        self.assertEqual(self.test_task1.budget, self.data["budget"])

    def test_sholud_return_non_context_when_no_user_is_log_in(self):
        self.client.logout()
        response = client.get(
            reverse("task-edit", kwargs={"pk": self.test_task1.id}), follow=True
        )

        self.assertRedirects(
            response, f"/users/accounts/login/?next=/tasks/edit/{self.test_task1.id}/"
        )
