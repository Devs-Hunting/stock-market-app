from django.contrib.auth.models import User
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from factories.factories import TaskFactory, UserFactory
from tasksapp.models import Task

client = Client()


class TestClientTaskListBaseView(TransactionTestCase):
    """
    Test case for the client task list view.
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. Here it prepares test user and tasks,
        logs in a user, and sets up a standard response object for use in the tests.
        """
        self.user = UserFactory.create()
        self.test_task1 = TaskFactory.create(client=self.user)
        self.test_task2 = TaskFactory.create(client=self.user)
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(reverse("tasks-client-list"))
        super().setUp()

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Task.objects.all().delete()

    def test_should_return_status_code_200_when_request_by_name(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a request is made.
        """
        self.assertEqual(self.response.status_code, 200)

    def test_should_check_that_view_use_correct_template(self):
        """
        Test whether the view uses the correct template.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/tasks_list.html")

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/tasks_list.html")
        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_task2, self.test_task1],
        )

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test whether the view paginates the results when there are more than ten items.
        """
        for _ in range(11):
            TaskFactory.create(client=self.user)

        response = self.client.get(reverse("tasks-client-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

    def test_should_redirect_if_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page if a not-logged-in user attempts to access it.
        """
        self.client.logout()
        self.response = self.client.get(reverse("tasks-client-list"))
        self.assertRedirects(self.response, "/users/accounts/login/?next=/tasks/")

    def test_elements_should_be_sorted_by_id_from_newest(self):
        """
        Test whether the returned tasks are sorted by id from newest.
        """
        self.assertEqual(list(self.response.context["object_list"])[0], self.test_task2)

    def test_should_return_objects_filtered_by_phrase_in_task_title(self):
        """
        Test whether the view returns tasks filtered by a phrase present in the task title.
        """
        self.test_task1 = TaskFactory.create(client=self.user, title="UniqueTitle1")
        self.test_task2 = TaskFactory.create(client=self.user, title="UniqueTitle2")

        filter_word = self.test_task2.title
        response_filter = self.client.get(
            reverse("tasks-client-list"), {"q": filter_word}
        )
        self.assertQuerysetEqual(
            response_filter.context["object_list"], [self.test_task2]
        )

    def test_should_return_objects_filterd_by_phrases_in_task_description(self):
        """
        Test whether the view returns tasks filtered by a phrase present in the task description.
        """
        filter_word = self.test_task2.description[0:10]

        response_filter = self.client.get(
            reverse("tasks-client-list"), {"q": filter_word}
        )
        self.assertQuerysetEqual(
            response_filter.context["object_list"], [self.test_task2]
        )


class TestClientTasksCurrentListView(TestCase):
    """
    Test case for the client's current task list view.
    """

    @classmethod
    def setUpClass(cls):
        cls.user = UserFactory.create()
        cls.test_task1 = TaskFactory.create(client=cls.user)
        cls.test_task2 = TaskFactory.create(client=cls.user)
        super().setUpClass()

    def setUp(self):
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(reverse("tasks-client-list"))
        super().setUp()

    def test_should_return_only_active_task(self):
        """
        Test whether the view returns only active tasks.
        """
        tasks_list = [self.test_task2, self.test_task1]

        self.assertEqual(list(self.response.context["object_list"]), tasks_list)
        self.assertEqual(len(self.response.context["object_list"]), 2)


class TestClientTasksHistoricalListView(TestCase):
    """
    Test case for the client's historical task list view.
    """

    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory.create()
        self.test_task1 = TaskFactory.create(client=self.user)
        self.test_task2 = TaskFactory.create(client=self.user)
        # self.client.login(username=self.user.username, password="secret")
        # self.response = self.client.get(reverse("tasks-client-history-list"))

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def test_should_return_only_task_with_status_completed_and_cancelld(self):
        """
        Test whether the view returns only tasks with status either 'completed' or 'cancelled'.
        """
        self.test_task2.status = 4
        self.test_task2.save()
        self.test_task2.refresh_from_db()

        self.client.login(username=self.user.username, password="secret")
        self.client.force_login(self.user)
        self.response = self.client.get(reverse("tasks-client-history-list"))

        self.assertEqual(list(self.response.context["object_list"]), [self.test_task2])

        self.assertEqual(len(self.response.context["object_list"]), 1)


class TestClientTaskCreateView(TestCase):
    """
    Test case for the client's task create view.
    """

    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory.create()
        # self.client.login(username=self.user.username, password="secret")
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

    def test_should_return_status_code_200_when_request_is_sent(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a GET request is made.
        """
        response = self.client.get(reverse("task-create"))

        self.assertEqual(response.status_code, 200)

    def test_should_create_task_object(self):
        """
        Test whether a new task object is created after a POST request is made.
        """
        response = self.client.post(reverse("task-create"), data=self.data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Task.objects.filter(title=self.data["title"]).count(), 1)

    def test_should_redirect_to_proper_url_after_success(self):
        """
        Test whether the view redirects to the correct URL after a successful task creation.
        """
        response = self.client.post(reverse("task-create"), data=self.data, follow=True)

        self.assertRedirects(
            response,
            reverse("tasks-client-list"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_sholud_return_non_context_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = client.get(reverse("task-create"))

        self.assertRedirects(response, "/users/accounts/login/?next=/tasks/add/")


class TestClientTaskEditView(TestCase):
    """
    Test case for the client's task edit view.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="testuser", password="12345")
        self.user.set_password("hello")
        self.user.save()
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            realization_time="2022-12-31",
            budget=1000.00,
            client=self.user,
            status=0,
        )

    def test_should_update_task_and_redirect_to_task_detail_view(self):
        """
        Test whether the edit view successfully updates a task object and redirects to the task detail view.
        """
        self.client.login(username="testuser", password="hello")

        response = self.client.post(
            reverse("task-edit", kwargs={"pk": self.task.pk}),
            {
                "title": "Updated Task",
                "description": "Updated Description",
                "realization_time": "2022-12-31",
                "budget": 2000.00,
                "status": 1,
            },
        )

        self.assertRedirects(
            response, reverse("task-detail", kwargs={"pk": self.task.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")
        self.assertEqual(self.task.budget, 2000.00)


class TestClientTaskEditViewTest(TestCase):
    """
    Test case for the client's task edit view with factory-based setup.
    """

    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory.create()
        self.test_task1 = TaskFactory.create(client=self.user)
        self.client.login(username=self.user.username, password="secret")
        # self.client.force_login(self.user)
        self.data = {
            "title": "Task Title",
            "description": "Task descrption",
            "realization_time": "2023-12-31",
            "budget": 1220.12,
        }

    def test_should_return_status_code_302_when_request_is_sent(self):
        """
        Test whether the edit view returns a HTTP 302 Redirect status code when a POST request is made.
        """
        response = self.client.post(
            reverse("task-edit", kwargs={"pk": self.test_task1.id}),
            {
                "title": "Updated Task",
                "description": "Updated Description",
                "realization_time": "2022-12-31",
                "budget": 2000.00,
                "status": 1,
            },
        )

        self.assertEqual(response.status_code, 302)

    def test_should_update_existing_task_object(self):
        """
        Test whether an existing task object is updated correctly after a POST request is made.
        """
        response = self.client.post(
            reverse("task-edit", kwargs={"pk": self.test_task1.id}),
            {
                "title": "Updated Task",
                "description": "Updated Description",
                "realization_time": "2022-12-31",
                "budget": 2000.00,
                "status": 1,
            },
        )

        self.assertRedirects(
            response, reverse("task-detail", kwargs={"pk": self.test_task1.pk})
        )
        self.test_task1.refresh_from_db()
        self.assertEqual(self.test_task1.title, "Updated Task")
        self.assertEqual(self.test_task1.budget, 2000.00)

    def test_sholud_return_non_context_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = client.get(
            reverse("task-edit", kwargs={"pk": self.test_task1.id}), follow=True
        )
        self.assertRedirects(
            response, f"/users/accounts/login/?next=/tasks/{self.test_task1.id}"
        )
