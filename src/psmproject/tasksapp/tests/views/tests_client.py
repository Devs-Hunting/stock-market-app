from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from factories.factories import OfferFactory, SolutionFactory, TaskFactory, UserFactory
from tasksapp.models import Offer, Solution, Task
from tasksapp.views.client import SKILL_PREFIX
from usersapp.helpers import skills_from_text
from usersapp.models import Skill

client = Client()


class TestClientTaskListBaseView(TestCase):
    """
    Test case for the client task list view.
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. Here it prepares test user and tasks,
        logs in a user, and sets up a standard response object for use in the tests.
        """
        super().setUp()
        self.user = UserFactory.create()
        self.test_task1 = TaskFactory.create(client=self.user)
        self.test_task2 = TaskFactory.create(client=self.user)
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(reverse("tasks-client-list"))

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Task.objects.all().delete()
        super().tearDown()

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
        response_filter = self.client.get(reverse("tasks-client-list"), {"q": filter_word})
        self.assertQuerysetEqual(response_filter.context["object_list"], [self.test_task2])

    def test_should_return_objects_filterd_by_phrases_in_task_description(self):
        """
        Test whether the view returns tasks filtered by a phrase present in the task description.
        """
        filter_word = self.test_task2.description[0:10]

        response_filter = self.client.get(reverse("tasks-client-list"), {"q": filter_word})
        self.assertQuerysetEqual(response_filter.context["object_list"], [self.test_task2])


class TestClientTasksCurrentListView(TestCase):
    """
    Test case for the client's current task list view.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory.create()
        cls.test_task1 = TaskFactory.create(client=cls.user)
        cls.test_task2 = TaskFactory.create(client=cls.user)

    def setUp(self):
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(reverse("tasks-client-list"))

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

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.skills = ["django", "flask", "javascript"]
        for skill in cls.skills:
            Skill.objects.create(skill=skill)

    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory.create()
        self.client.force_login(self.user)
        skills_data = {}
        for index in range(len(self.skills)):
            skills_data[f"{SKILL_PREFIX}{index}"] = self.skills[index]
        self.data = {
            "title": "Task Title",
            "description": "Task descrption",
            "days_to_complete": 31,
            "budget": 1220.12,
        }
        self.data.update(skills_data)

    @classmethod
    def tearDownClass(cls):
        Skill.objects.all().delete()
        super().tearDownClass()

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

    def test_should_add_skills_to_task(self):
        """
        Test if skills given as a string are added to m2m relation of a newly created task
        """
        response = self.client.post(reverse("task-create"), data=self.data, follow=True)

        self.assertEqual(response.status_code, 200)
        task = Task.objects.get(title=self.data["title"])
        self.assertEqual(task.skills.count(), len(self.skills))
        skills_strings = set([skill.skill for skill in task.skills.all()])
        self.assertSetEqual(skills_strings, set(self.skills))

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

    def test_should_return_non_context_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = client.get(reverse("task-create"))

        self.assertRedirects(response, "/users/accounts/login/?next=/tasks/add/")

    def test_should_block_access_for_blocked_user_and_redirect_to_dashboard(self):
        """
        Test whether the view correctly redirects to the dashboard page when a blocked user attempts to access it.
        """
        blocked_user_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("BLOCKED_USER"))
        self.user.groups.add(blocked_user_group)
        response = self.client.get(reverse("task-create"))

        self.assertRedirects(response, reverse("dashboard"))


class TestClientTaskEditView(TestCase):
    """
    Test case for the client's task edit view.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.available_skills = ["django", "python", "flask", "microservices", "sql"]
        for skill in cls.available_skills:
            Skill.objects.create(skill=skill)

    def setUp(self):
        super().setUp()
        self.client = Client()
        self.user = User.objects.create(username="testuser", password="12345")
        self.user.set_password("hello")
        self.user.save()
        existing_skills = self.available_skills[:3]
        skills = skills_from_text(existing_skills)
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            days_to_complete=31,
            budget=1000.00,
            client=self.user,
            status=0,
        )
        self.task.skills.set(skills)

    @classmethod
    def tearDownClass(cls):
        Skill.objects.all().delete()
        super().tearDownClass()

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
                "days_to_complete": 31,
                "budget": 2000.00,
                "status": 1,
                f"{SKILL_PREFIX}14": self.available_skills[1],
                f"{SKILL_PREFIX}15": self.available_skills[4],
            },
        )

        self.assertRedirects(response, reverse("task-detail", kwargs={"pk": self.task.pk}))
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")
        self.assertEqual(self.task.budget, 2000.00)
        self.assertEqual(self.task.skills.count(), 2)
        skills_strings = set([skill.skill for skill in self.task.skills.all()])
        self.assertSetEqual(skills_strings, {self.available_skills[1], self.available_skills[4]})

    def test_should_remove_skills_from_task_if_no_skill_given_in_post(self):
        """
        Test whether the edit view successfully updates a task object and redirects to the task detail view.
        """
        self.client.login(username="testuser", password="hello")

        self.client.post(
            reverse("task-edit", kwargs={"pk": self.task.pk}),
            {
                "title": self.task.title,
                "description": self.task.description,
                "days_to_complete": self.task.days_to_complete,
                "budget": self.task.budget,
                "status": self.task.status,
            },
        )
        self.task.refresh_from_db()
        self.assertEqual(self.task.skills.count(), 0)


class TestClientTaskEditViewTest(TestCase):
    """
    Test case for the client's task edit view with factory-based setup.
    """

    def setUp(self) -> None:
        super().setUp()
        self.user = UserFactory.create()
        self.test_task1 = TaskFactory.create(client=self.user)
        self.client.login(username=self.user.username, password="secret")
        self.data = {
            "title": "Task Title",
            "description": "Task descrption",
            "days_to_complete": 31,
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
                "days_to_complete": 31,
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
                "days_to_complete": 31,
                "budget": 2000.00,
                "status": 1,
            },
        )

        self.assertRedirects(response, reverse("task-detail", kwargs={"pk": self.test_task1.pk}))
        self.test_task1.refresh_from_db()
        self.assertEqual(self.test_task1.title, "Updated Task")
        self.assertEqual(self.test_task1.budget, 2000.00)

    def test_should_return_non_context_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = client.get(reverse("task-edit", kwargs={"pk": self.test_task1.id}), follow=True)
        self.assertRedirects(response, f"/users/accounts/login/?next=/tasks/{self.test_task1.id}/edit")

    def test_should_block_access_for_blocked_user_and_redirect_to_dashboard(self):
        """
        Test whether the view correctly redirects to the dashboard page when a blocked user attempts to access it.
        """
        blocked_user_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("BLOCKED_USER"))
        self.user.groups.add(blocked_user_group)
        response = self.client.post(reverse("task-edit", kwargs={"pk": self.test_task1.id}), follow=True)

        self.assertRedirects(response, reverse("dashboard"))


class TestOfferClientListView(TestCase):
    """
    Test case for list view of offers for all tasks created by currently logged-in user (client).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.test_client = UserFactory.create()
        cls.test_task1 = TaskFactory.create(client=cls.test_client)
        cls.contractor = UserFactory.create()
        cls.contractor2 = UserFactory.create()
        cls.test_offer1 = OfferFactory.create(contractor=cls.contractor, task=cls.test_task1)
        cls.test_offer2 = OfferFactory.create(contractor=cls.contractor2, task=cls.test_task1)

    def setUp(self):
        super().setUp()
        self.client.login(username=self.test_client.username, password="secret")
        self.response = self.client.get(reverse("offers-client-list"))

    @classmethod
    def tearDownClass(cls) -> None:
        Task.objects.all().delete()
        Offer.objects.all().delete()
        super().tearDownClass()

    def test_should_check_that_view_use_correct_template(self):
        """
        Test check if the view use correct template and response HTTP is 200.
        """

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/offers_list_client.html")

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test check if the view return correct objects when a request is sent.
        """

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/offers_list_client.html")
        self.assertEqual(list(self.response.context["object_list"]), [self.test_offer2, self.test_offer1])

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test check if the view has pagination when there are more than ten elements.
        """
        for _ in range(11):
            temp_user = UserFactory.create()
            OfferFactory.create(contractor=temp_user, task=self.test_task1)

        new_response = self.client.get(reverse("offers-client-list"))
        self.assertEqual(new_response.status_code, 200)
        self.assertContains(new_response, 'href="?page=2"')
        self.assertEqual(len(new_response.context["object_list"]), 10)

    def test_should_redirect_if_not_logged_in(self):
        """
        Test checks that the view correct redirects when a non logged user attempts to access it.
        """
        self.client.logout()
        new_response = self.client.get(reverse("offers-client-list"))
        self.assertRedirects(new_response, "/users/accounts/login/?next=/tasks/offers/client/")

    def test_should_return_elements_sorted_by_id_from_newest(self):
        """
        Test checks that the view return elements sorted by id from newest.
        """

        self.assertEqual(list(self.response.context["object_list"])[0], self.test_offer2)

    def test_should_return_only_elements_with_selected_offer_with_value_none(self):
        """
        Test checks that the view return only offers for tasks that has no selected offer.
        Task attribute selected_offer is set to None.
        """
        new_task = TaskFactory(client=self.test_client)
        selected_offer = OfferFactory.create(task=new_task, accepted=True)
        new_task.selected_offer = selected_offer
        new_task.save()

        new_response = self.client.get(reverse("offers-client-list"))
        self.assertEqual(list(new_response.context["object_list"]), [self.test_offer2, self.test_offer1])
        self.assertNotEqual(list(new_response.context["object_list"])[0], [selected_offer])

    def test_should_return_objects_filtered_by_phrases_in_offer_description(self):
        """
        Test check that view return objects filtered by phrases in offer description.
        """
        self.test_offer3 = OfferFactory.create(
            contractor=self.contractor, task=self.test_task1, description="UniqueDescription"
        )
        filter_word = self.test_offer3.description

        response_filter = self.client.get(reverse("offers-client-list"), {"q": filter_word})
        self.assertQuerySetEqual(response_filter.context["object_list"], [self.test_offer3])

    def test_should_return_objects_filtered_by_phrases_in_task_title(self):
        """
        Test check that view return objects filtered by phrases in task title.
        """
        filter_word = self.test_task1.title

        response_filter = self.client.get(reverse("offers-client-list"), {"q": filter_word})
        self.assertEqual(list(response_filter.context["object_list"])[0], self.test_offer2)

    def test_should_return_objects_filtered_by_phrases_in_contractor_username(self):
        """
        Test check that view return objects filtered by phrases in contractor username.
        """
        filter_word = self.contractor.username

        response_filter = self.client.get(reverse("offers-client-list"), {"q": filter_word})
        self.assertEqual(list(response_filter.context["object_list"])[0], self.test_offer1)

    def test_should_return_objects_filtered_by_phrases_in_task_description(self):
        """
        Test check that view return objects filtered by phrases in task description.
        """
        filter_word = self.test_task1.description

        response_filter = self.client.get(reverse("offers-client-list"), {"q": filter_word})
        self.assertEqual(list(response_filter.context["object_list"])[0], self.test_offer2)


class TestTaskOfferClientListView(TestCase):
    """
    Test case for list view of offers for only one task created by currently logged-in user (client).
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.test_client = UserFactory.create()
        cls.test_task1 = TaskFactory.create(client=cls.test_client)
        cls.contractor = UserFactory.create()
        cls.contractor2 = UserFactory.create()
        cls.test_offer1 = OfferFactory.create(contractor=cls.contractor, task=cls.test_task1)
        cls.test_offer2 = OfferFactory.create(contractor=cls.contractor2, task=cls.test_task1)

    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.test_client.username, password="secret")
        self.response = self.client.get(reverse("task-offers-list", kwargs={"pk": self.test_task1.id}))

    @classmethod
    def tearDownClass(cls) -> None:
        Task.objects.all().delete()
        Offer.objects.all().delete()
        super().tearDownClass()

    def test_should_check_that_view_use_correct_template(self):
        """
        Test check if the view use correct template and response HTTP is 200.
        """

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/offers_list_client_task.html")

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test check if the view return correct objects when a request is sent.
        It should be offers and the task object.
        """

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/offers_list_client_task.html")
        self.assertEqual(list(self.response.context["object_list"]), [self.test_offer2, self.test_offer1])
        self.assertEqual(self.response.context["task"], self.test_task1)

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test check if the view has pagination when there are more than ten elements.
        """
        for _ in range(11):
            temp_user = UserFactory.create()
            OfferFactory.create(contractor=temp_user, task=self.test_task1)

        new_response = self.client.get(reverse("task-offers-list", kwargs={"pk": self.test_task1.id}))
        self.assertEqual(new_response.status_code, 200)
        self.assertContains(new_response, 'href="?page=2"')
        self.assertEqual(len(new_response.context["object_list"]), 10)

    def test_should_redirect_if_not_logged_in(self):
        """
        Test checks that the view correct redirects when a non logged user attempts to access it.
        """
        self.client.logout()
        new_response = self.client.get(reverse("task-offers-list", kwargs={"pk": self.test_task1.id}))
        self.assertRedirects(new_response, f"/users/accounts/login/?next=/tasks/{self.test_task1.id}/offers/")

    def test_should_return_objects_filtered_by_phrases_in_offer_description(self):
        """
        Test check that view return objects filtered by phrases in offer description.
        """
        self.test_offer3 = OfferFactory.create(
            contractor=self.contractor, task=self.test_task1, description="UniqueDescription"
        )
        filter_word = self.test_offer3.description

        response_filter = self.client.get(
            reverse("task-offers-list", kwargs={"pk": self.test_task1.id}), {"q": filter_word}
        )
        self.assertQuerySetEqual(response_filter.context["object_list"], [self.test_offer3])

    def test_should_return_objects_filtered_by_phrases_in_contractor_username(self):
        """
        Test check that view return objects filtered by phrases in contractor username.
        """
        filter_word = self.contractor.username

        response_filter = self.client.get(
            reverse("task-offers-list", kwargs={"pk": self.test_task1.id}), {"q": filter_word}
        )
        self.assertEqual(list(response_filter.context["object_list"])[0], self.test_offer1)


class TestOfferClientAcceptView(TestCase):
    """
    Test case for view to accept offer by client.
    """

    def setUp(self) -> None:
        super().setUp()
        self.client = Client()
        self.test_client = UserFactory.create()
        self.test_task1 = TaskFactory.create(client=self.test_client, selected_offer=None)
        self.contractor = UserFactory.create()
        self.test_offer = OfferFactory.create(contractor=self.contractor, task=self.test_task1)
        self.client.login(username=self.test_client.username, password="secret")
        self.response = self.client.post(reverse("offer-client-accept", kwargs={"pk": self.test_offer.id}))

    def tearDown(self) -> None:
        Task.objects.all().delete()
        Offer.objects.all().delete()
        super().tearDown()

    def test_should_update_task_and_offer_and_redirect_to_offer_detail(self):
        """
        Test check that view updated offer (accepted to True and realization time populated with today date + value
        from days_to_complete field) and task (status to on-going and selected_offer to the offer object) and is
        properly redirected to offer detail page.
        """
        self.test_task1.refresh_from_db()
        self.test_offer.refresh_from_db()

        self.assertRedirects(self.response, reverse("offer-detail", kwargs={"pk": self.test_offer.id}))
        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.test_task1.selected_offer, self.test_offer)
        self.assertEqual(self.test_offer.accepted, True)
        self.assertEqual(self.test_task1.status, Task.TaskStatus.ON_GOING)
        self.assertEqual(
            self.test_task1.selected_offer.realization_time,
            date.today() + timedelta(days=self.test_task1.selected_offer.days_to_complete),
        )

    def test_should_block_update_of_task_and_offer_if_task_has_selected_offer(self):
        """
        Test check that view does not update offer and task when task has already selected offer.
        """
        self.test_task1.refresh_from_db()
        self.test_offer.refresh_from_db()
        contractor2 = UserFactory.create()
        test_offer2 = OfferFactory.create(contractor=contractor2, task=self.test_task1)
        another_offer_response = self.client.post(reverse("offer-client-accept", kwargs={"pk": test_offer2.id}))

        self.assertRedirects(another_offer_response, reverse("offers-client-list"))
        self.assertEqual(self.test_task1.selected_offer, self.test_offer)
        self.assertEqual(another_offer_response.status_code, 302)

    def test_should_block_accept_offer_if_user_is_not_client(self):
        """
        Test check that view is blocked when user is not client.
        """
        test_task3 = TaskFactory.create(client=self.test_client, selected_offer=None)
        test_offer2 = OfferFactory.create(contractor=self.contractor, task=test_task3)
        user_not_client = UserFactory.create()
        self.client.logout()
        self.client.force_login(user_not_client)
        new_response = self.client.post(reverse("offer-client-accept", kwargs={"pk": test_offer2.id}))

        self.assertRedirects(new_response, reverse("dashboard"))
        test_task3.refresh_from_db()
        self.assertEqual(test_task3.selected_offer, None)

    def test_should_block_access_for_blocked_user_and_redirect_to_dashboard(self):
        """
        Test whether the view correctly redirects to the dashboard page when a blocked user attempts to access it.
        """
        test_task3 = TaskFactory.create(client=self.test_client, selected_offer=None)
        test_offer2 = OfferFactory.create(contractor=self.contractor, task=test_task3)
        blocked_user_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("BLOCKED_USER"))
        self.test_client.groups.add(blocked_user_group)
        new_response = self.client.post(reverse("offer-client-accept", kwargs={"pk": test_offer2.id}))

        self.assertRedirects(new_response, reverse("dashboard"))


class TestSolutionClientAcceptView(TestCase):
    """
    Test case for view to accept solution by client.
    """

    def setUp(self) -> None:
        super().setUp()
        self.client = Client()
        self.client_user = UserFactory.create()
        self.test_task = TaskFactory.create(client=self.client_user, selected_offer=None)
        self.contractor = UserFactory.create()
        self.test_offer = OfferFactory.create(contractor=self.contractor, task=self.test_task)
        self.test_solution = SolutionFactory.create()
        self.test_offer.solution = self.test_solution
        self.test_offer.save()

        self.client.login(username=self.client_user.username, password="secret")
        self.url = reverse("solution-accept", kwargs={"pk": self.test_solution.id})
        self.response = self.client.post(self.url)

    def tearDown(self) -> None:
        Task.objects.all().delete()
        Offer.objects.all().delete()
        Solution.objects.all().delete()
        super().tearDown()

    def test_should_update_task_and_solution_and_redirect_to_task_detail(self):
        """
        Test check that view updated solution (accepted to True) and task (status to completed) and is properly
        redirected to task detail page.
        """
        self.test_task.refresh_from_db()
        self.test_solution.refresh_from_db()

        self.assertEqual(self.response.status_code, 302)
        self.assertEqual(self.test_solution.accepted, True)
        self.assertEqual(self.test_task.status, Task.TaskStatus.COMPLETED)
        self.assertRedirects(self.response, reverse("task-detail", kwargs={"pk": self.test_task.id}))

    def test_should_block_accept_solution_if_user_is_not_client(self):
        """
        Test check that view is blocked when user is not client.
        """

        self.client.login(username=self.contractor.username, password="secret")
        self.url = reverse("solution-accept", kwargs={"pk": self.test_solution.id})
        response = self.client.post(self.url)
        self.assertRedirects(response, reverse("dashboard"))

        self.client.logout()
        response_logout = self.client.post(self.url)
        self.assertRedirects(response_logout, f"/users/accounts/login/?next={self.url}")

    def test_should_block_access_for_blocked_user_and_redirect_to_dashboard(self):
        """
        Test whether the view correctly redirects to the dashboard page when a blocked user attempts to access it.
        """
        self.test_task2 = TaskFactory.create(client=self.client_user, selected_offer=None)
        self.test_offer2 = OfferFactory.create(contractor=self.contractor, task=self.test_task2)
        self.test_solution2 = SolutionFactory.create()
        self.test_offer2.solution = self.test_solution2
        self.test_offer2.save()
        blocked_user_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("BLOCKED_USER"))
        self.client_user.groups.add(blocked_user_group)
        new_response = self.client.post(reverse("solution-accept", kwargs={"pk": self.test_solution2.id}))

        self.assertRedirects(new_response, reverse("dashboard"))
