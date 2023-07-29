from django.contrib.auth.models import Group, User
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse
from tasksapp.models import Task
from tasksapp.tests.views.factories import TaskFactory, UserFactory

client = Client()


class TestModeratorTaskListView(TransactionTestCase):
    "Test case for moderator task list view."

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. Here it prepares test user and tasks,
        logs in a user, and sets up a standard response object for use in the tests.
        """
        self.user_client = UserFactory.create()
        self.user_moderator = UserFactory.create()
        moderator_group = Group.objects.create(name="MODERATOR")
        self.user_moderator.groups.add(moderator_group)
        self.test_task1 = TaskFactory.create(client=self.user_client)
        self.test_task2 = TaskFactory.create(client=self.user_client)
        self.client.login(username=self.user_moderator.username, password="secret")
        self.response = self.client.get(reverse("tasks-moderator-list"))
        super().setUp()

    def tearDown(self) -> None:
        """
        Clean up method after each test case.
        """
        Task.objects.all().delete()

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
        TaskFactory.create_batch(10, client=self.user_client)

        response = self.client.get(reverse("tasks-moderator-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

    def test_should_make_redirect_to_proper_address_when_user_has_no_permission_to_use_view(
        self,
    ):
        """
        Tests checks if the user is redirected to the proper address when they do not have permission to use the view.
        """
        self.user_client = UserFactory.create()
        client_group = Group.objects.create(name="CLIENT")
        self.user_client.groups.add(client_group)
        self.client.login(username=self.user_client.username, password="secret")

        response_client = self.client.get(reverse("tasks-moderator-list"))
        self.assertEqual(response_client.status_code, 302)
        self.assertRedirects(response_client, "/")

    def test_should_redirect_if_not_logged_in(self):
        """
        Tests checks if the user is redirected to the proper address when they do not have permission to use the view.
        """
        self.client.logout()
        self.response = self.client.get(reverse("tasks-moderator-list"))
        self.assertRedirects(self.response, "/")

    def test_should_return_correct_objects_when_request_is_sent_from_user_in_allowed_groups(
        self,
    ):
        """
        Tests checks if the correct objects are returned when a request is sent to the view
        from users in allowed groups.
        """
        self.user_administrator = UserFactory.create()
        administrator_group = Group.objects.create(name="ADMINISTRATOR")
        self.user_administrator.groups.add(administrator_group)
        self.user_arbiter = UserFactory.create()
        arbiter_group = Group.objects.create(name="ARBITER")
        self.user_arbiter.groups.add(arbiter_group)

        for role in [self.user_moderator, self.user_administrator, self.user_arbiter]:

            self.client.login(username=role, password="secret")
            self.assertEqual(self.response.status_code, 200)
            self.assertTemplateUsed(self.response, "tasksapp/tasks_list_all.html")
            self.assertEqual(
                list(self.response.context["object_list"]),
                [self.test_task2, self.test_task1],
            )

    def test_should_return_objects_filtered_by_phrases_in_task_title(self):
        """
        Test checks the filtering of objects based on phrases present in the task title.
        """
        self.test_task1 = TaskFactory.create(
            client=self.user_client, title="UniqueTitle1"
        )
        self.test_task2 = TaskFactory.create(
            client=self.user_client, title="UniqueTitle2"
        )

        filter_word = self.test_task2.title
        response_filter = self.client.get(
            reverse("tasks-moderator-list"), {"q": filter_word}
        )
        self.assertQuerysetEqual(
            response_filter.context["object_list"], [self.test_task2]
        )

    def test_should_return_object_filtered_by_phrases_in_task_description(self):
        """
        Test checks the filtering of objects based on phrases in the task description.
        """
        filter_word = self.test_task1.description[0:10]
        response_filter = self.client.get(
            reverse("tasks-moderator-list"), {"q": filter_word}
        )

        self.assertQuerysetEqual(
            response_filter.context["object_list"], [self.test_task1]
        )

    def test_should_return_tasks_filtered_by_user_id(self):
        """
        This tests checks the filtering of tasks based on user ID.
        """

        task_list_user_client = Task.objects.filter(client_id=self.user_client.id)
        response_filter = self.client.get(
            reverse("tasks-moderator-list"), {"q": self.user_client.id}
        )
        self.assertQuerysetEqual(
            response_filter.context["object_list"], task_list_user_client[::-1]
        )


class TestModeratorTaskEditView(TestCase):
    """
    Test case for the task edit view only by the moderator.
    """

    def setUp(self):
        """
        Set up method that is run before every task. Here it prepares test user, task and
        user in role moderator.
        """
        self.client = Client()
        self.user = User.objects.create(username="testuser", password="12345")
        self.user_moderator = User.objects.create(
            username="moderator_test", password="123456"
        )
        moderator_group = Group.objects.create(name="MODERATOR")
        self.user_moderator.groups.add(moderator_group)
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            realization_time="2022-12-31",
            budget=1000.00,
            client=self.user,
            status=0,
        )

    def test_should_return_correct_status_code(self):
        """
        Test whether the edit view returns a HTTP 302 Redirect status code when a POST request is made.
        """
        self.client.login(username=self.user_moderator.username, password="123456")

        response = self.client.post(
            reverse("task-moderator-edit", kwargs={"pk": self.task.id}),
            {
                "title": "Updated Task",
                "description": "Updated Description",
                "status": 1,
            },
        )

        self.assertEqual(response.status_code, 302)

    def test_should_update_task_and_redirect_to_task_detail_view(self):
        """
        Test whether the edit view successfully updates a task object and redirects to the task detail view.
        """
        self.client.login(username=self.user_moderator.username, password="123456")
        self.client.force_login(self.user_moderator)
        response = self.client.post(
            reverse("task-moderator-edit", kwargs={"pk": self.task.id}),
            {
                "title": "Updated Task",
                "description": "Updated Description",
                "status": 1,
            },
        )

        self.assertRedirects(
            response, reverse("task-detail", kwargs={"pk": self.task.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")
        self.assertEqual(self.task.status, 1)


class TestModeratorTaskEditViewTest(TestCase):
    """
    Test case for the task edit view only by the moderator with factory-based setup.
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every task. Here it prepares with use of Factory
        a test user, tasks and user as moderator.
        """
        super().setUp()
        self.user = UserFactory.create()
        self.user_moderator = UserFactory.create()
        moderator_group = Group.objects.create(name="MODERATOR")
        self.user_moderator.groups.add(moderator_group)
        self.test_task1 = TaskFactory.create(client=self.user)
        self.client.login(username=self.user_moderator.username, password="secret")
        self.data = {
            "title": "Updated Task",
            "description": "Updated Description",
            "status": 1,
        }

    def test_should_return_status_code_302_when_request_is_sent(self):
        """
        Test whether the edit view returns a HTTP 302 Redirect status code when a POST request is made.
        """
        response = self.client.post(
            reverse("task-moderator-edit", kwargs={"pk": self.test_task1.id}),
            self.data,
        )

        self.assertEqual(response.status_code, 302)

    def test_should_update_existing_task_object(self):
        """
        Test whether an existing task object is updated correctly after a POST request is made.
        """
        response = self.client.post(
            reverse("task-moderator-edit", kwargs={"pk": self.test_task1.id}),
            {
                "title": "Updated Task",
                "description": "Updated Description",
                "status": 1,
            },
        )

        self.assertRedirects(
            response, reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )
        self.test_task1.refresh_from_db()
        self.assertEqual(self.test_task1.title, "Updated Task")
        self.assertEqual(self.test_task1.status, 1)

    def test_should_return_non_context_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non logged in user
        attempts to access the view.
        """
        self.client.logout()
        response = client.get(
            reverse("task-moderator-edit", kwargs={"pk": self.test_task1.id}),
            follow=True,
        )
        self.assertRedirects(
            response, f"/users/accounts/login/?next=/tasks/{self.test_task1.id}"
        )

    def test_should_check_that_user_in_role_arbiter_administrator_can_not_update_task(
        self,
    ):
        """
        Test checks that user in role arbiter or administrator can not update task.
        """
        self.user_administrator = UserFactory.create()
        administrator_group = Group.objects.create(name="ADMINISTRATOR")
        self.user_administrator.groups.add(administrator_group)
        self.user_arbiter = UserFactory.create()
        arbiter_group = Group.objects.create(name="ARBITER")
        self.user_arbiter.groups.add(arbiter_group)

        for role in [self.user_administrator, self.user_arbiter]:

            self.client.login(username=role, password="secret")
            response_role = self.client.post(
                reverse("task-moderator-edit", kwargs={"pk": self.test_task1.id}),
                {
                    "title": "Updated Task",
                    "description": "Updated Description",
                    "status": 1,
                },
                follow=True,
            )

            self.assertEqual(response_role.status_code, 200)
            self.test_task1.refresh_from_db()
            self.assertNotEqual(self.test_task1.title, "Updated Task")
            self.assertRedirects(response_role, f"/tasks/{self.test_task1.id}")

    def test_should_check_that_moderator_could_not_change_budget_client_realization_time(
        self,
    ):
        """
        Test checks that the budget and realization time cannot be changed by the moderator.
        """
        user2 = UserFactory.create()

        response = self.client.post(
            reverse("task-moderator-edit", kwargs={"pk": self.test_task1.id}),
            {
                "title": "Updated Task",
                "description": "Updated Description",
                "realization_time": "2023-12-31",
                "budget": 2000.00,
                "status": 1,
                "client": user2,
            },
        )

        self.assertRedirects(
            response, reverse("task-detail", kwargs={"pk": self.test_task1.id})
        )
        self.test_task1.refresh_from_db()
        self.assertEqual(self.test_task1.title, "Updated Task")
        self.assertEqual(self.test_task1.client, self.user)
        self.assertNotEqual(self.test_task1.status, "2023-12-31")
        self.assertNotEqual(self.test_task1.budget, 2000.00)
