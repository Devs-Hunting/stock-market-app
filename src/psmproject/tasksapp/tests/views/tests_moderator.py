from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from factories.factories import OfferFactory, TaskFactory, UserFactory
from tasksapp.models import Offer, Task
from usersapp.models import Skill

client = Client()


class TestModeratorTaskListView(TestCase):
    "Test case for moderator task list view."

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse("tasks-moderator-list")

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. Here it prepares test user and tasks,
        logs in a user, and sets up a standard response object for use in the tests.
        """
        super().setUp()
        self.client = Client()
        self.user_client = UserFactory.create()
        self.user_moderator = UserFactory.create()
        moderator_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("MODERATOR"))
        self.user_moderator.groups.add(moderator_group)
        self.test_task1 = TaskFactory.create(
            client=self.user_client, title="UniqueTitle1", description="SpecialDescription1"
        )
        self.test_task2 = TaskFactory.create(
            client=self.user_client, title="UniqueTitle2", description="CompletlyDifferentText2"
        )
        self.client.login(username=self.user_moderator.username, password="secret")
        self.response = self.client.get(self.url)

    def tearDown(self) -> None:
        """
        Clean up method after each test case.
        """
        Task.objects.all().delete()
        super().tearDown()

    def test_should_return_correct_status_code_and_template_request_by_name(self):
        """
        This test case checks if the response status code is equal to 200 and if the correct template is used.
        """

        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "tasksapp/tasks_list_moderator.html")

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test verify that pagination is applied if there are more than ten elements.
        """
        TaskFactory.create_batch(10, client=self.user_client)

        response = self.client.get(self.url)
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
        self.client.login(username=self.user_client.username, password="secret")

        response_client = self.client.get(self.url)
        self.assertEqual(response_client.status_code, 302)
        self.assertRedirects(response_client, "/")

    def test_should_redirect_if_not_logged_in(self):
        """
        Tests checks if the user is redirected to the proper address when they do not have permission to use the view.
        """
        self.client.logout()

        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, f"/users/accounts/login/?next={self.url}")

    def test_should_return_correct_objects_when_request_is_sent_from_user_in_allowed_groups(
        self,
    ):
        """
        Tests checks if the correct objects are returned when a request is sent to the view
        from users in allowed groups.
        """
        self.client = Client()
        self.user_administrator = UserFactory.create()
        administrator_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("ADMINISTRATOR"))
        self.user_administrator.groups.add(administrator_group)
        self.user_arbiter = UserFactory.create()
        arbiter_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("ARBITER"))
        self.user_arbiter.groups.add(arbiter_group)

        for role in [self.user_moderator, self.user_administrator, self.user_arbiter]:
            self.client.login(username=role, password="secret")
            self.assertEqual(self.response.status_code, 200)
            self.assertTemplateUsed(self.response, "tasksapp/tasks_list_moderator.html")
            self.assertEqual(
                list(self.response.context["object_list"]),
                [self.test_task2, self.test_task1],
            )

    def test_should_return_form_on_get(self):
        form = self.response.context.get("form")
        self.assertIsNotNone(form)

    def test_should_return_tasks_filtered_by_title_when_query_posted(self):
        response = self.client.post(
            self.url,
            {
                "query": self.test_task1.title,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task1])

    def test_should_return_tasks_filtered_by_description_when_query_posted(self):
        response = self.client.post(
            self.url,
            {
                "query": self.test_task1.description[:10],
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_task1])

    def test_should_return_tasks_filtered_by_username_when_posted(self):
        another_user = UserFactory.create()
        test_task3 = TaskFactory.create(client=another_user)

        response = self.client.post(
            self.url,
            {
                "username": another_user.username,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [test_task3])


class TestModeratorTaskEditView(TestCase):
    """
    Test case for the task edit view only by the moderator.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.skill = Skill.objects.create(skill="Python")

    def setUp(self):
        """
        Set up method that is run before every task. Here it prepares test user, task and
        user in role moderator.
        """
        super().setUp()
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user_moderator = User.objects.create_user(username="moderator_test", password="123456")
        moderator_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("MODERATOR"))
        self.user_moderator.groups.add(moderator_group)
        self.client.login(username=self.user_moderator.username, password="123456")
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            realization_time="2022-12-31",
            budget=1000.00,
            client=self.user,
            status=0,
        )
        self.task.skills.add(self.skill)

    def tearDown(self):
        Task.objects.all().delete()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        Skill.objects.all().delete()
        super().tearDownClass()

    def test_should_return_correct_status_code(self):
        """
        Test whether the edit view returns a HTTP 302 Redirect status code when a POST request is made.
        """

        response = self.client.post(
            reverse("task-moderator-edit", kwargs={"pk": self.task.pk}),
            {
                "title": "Updated Task",
                "description": "Updated Description",
                "status": 1,
                "skills": [self.skill.id],
            },
        )

        self.assertEqual(response.status_code, 302)

    def test_should_update_task_and_redirect_to_task_detail_view(self):
        """
        Test whether the edit view successfully updates a task object and redirects to the task detail view.
        """
        response = self.client.post(
            reverse("task-moderator-edit", kwargs={"pk": self.task.id}),
            {
                "title": "Updated Task",
                "description": "Updated Description",
            },
        )

        self.assertRedirects(response, reverse("task-moderator-detail", kwargs={"pk": self.task.pk}))
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "Updated Task")
        self.assertEqual(self.task.description, "Updated Description")


class TestModeratorTaskEditViewFactoryTest(TestCase):
    """
    Test case for the task edit view only by the moderator with factory-based setup.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.skill = Skill.objects.create(skill="Python")
        cls.moderator_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("MODERATOR"))
        cls.user = UserFactory.create()
        cls.user_moderator = UserFactory.create()
        cls.user_moderator.groups.add(cls.moderator_group)

    def setUp(self) -> None:
        """
        Set up method that is run before every task. Here it prepares with use of Factory
        a test user, tasks and user as moderator.
        """
        super().setUp()
        self.client = Client()
        self.test_task1 = TaskFactory.create(client=self.user)
        self.client.login(username=self.user_moderator.username, password="secret")
        self.data = {
            "title": "Updated Task",
            "description": "Updated Description",
            "status": 1,
            "skills": [self.skill.id],
        }
        self.url = reverse("task-moderator-edit", kwargs={"pk": self.test_task1.id})

    def tearDown(self):
        Task.objects.all().delete()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        Skill.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def test_should_return_status_code_302_when_request_is_sent(self):
        """
        Test whether the edit view returns a HTTP 302 Redirect status code when a POST request is made.
        """

        response = self.client.post(
            self.url,
            {
                "title": "Updated Task",
                "description": "Updated Description",
                "status": 1,
                "skills": [self.skill.id],
            },
        )

        self.assertEqual(response.status_code, 302)

    def test_should_update_existing_task_object(self):
        """
        Test whether an existing task object is updated correctly after a POST request is made.
        """

        response = self.client.post(
            self.url,
            {
                "title": "Updated Task",
                "description": "Updated Description",
            },
        )

        self.assertRedirects(response, reverse("task-moderator-detail", kwargs={"pk": self.test_task1.id}))
        self.test_task1.refresh_from_db()
        self.assertEqual(self.test_task1.title, "Updated Task")
        self.assertEqual(self.test_task1.description, "Updated Description")

    def test_should_return_non_context_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non logged in user
        attempts to access the view.
        """
        self.client.logout()
        response = self.client.get(
            self.url,
            follow=True,
        )
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")

    def test_should_check_that_moderator_could_not_change_budget_client_realization_time(
        self,
    ):
        """
        Test checks that the budget and realization time cannot be changed by the moderator.
        """
        user2 = UserFactory.create()
        response = self.client.post(
            self.url,
            {
                "title": "Updated Task",
                "description": "Updated Description",
                "realization_time": "2023-12-31",
                "budget": 2000.00,
                "status": 1,
                "client": user2,
                "skills": [self.skill.id],
            },
        )

        self.assertRedirects(response, reverse("task-moderator-detail", kwargs={"pk": self.test_task1.id}))
        self.test_task1.refresh_from_db()
        self.assertEqual(self.test_task1.title, "Updated Task")
        self.assertEqual(self.test_task1.client, self.user)
        self.assertNotEqual(self.test_task1.status, "2023-12-31")
        self.assertNotEqual(self.test_task1.budget, 2000.00)


class TestModeratorOfferListView(TestCase):
    """
    Test case for the moderator offers' list view
    """

    url_name = "offer-moderator-list"
    template = "tasksapp/offers_list_moderator.html"

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up method that is run once for test case. It prepares skills, users, tasks for tests
        """
        super().setUpClass()
        skills = ["python", "django", "java script", "flask"]
        cls.skills = []
        for skill in skills:
            cls.skills.append(Skill.objects.create(skill=skill))
        cls.user = UserFactory.create()
        moderator_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("MODERATOR"))
        cls.user.groups.add(moderator_group)
        cls.contractor_user = UserFactory.create()
        cls.client_user = UserFactory.create()
        cls.test_task1 = TaskFactory.create(
            client=cls.client_user,
            title="UniqueTitle1",
        )
        cls.test_task2 = TaskFactory.create(
            client=cls.client_user,
            title="UniqueTitle2",
        )
        cls.url = reverse(TestModeratorOfferListView.url_name)

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. It prepares offers, logs in moderator and gets view
        response
        """
        super().setUp()

        self.test_offer1 = OfferFactory.create(contractor=self.contractor_user, task=self.test_task1, accepted=False)
        self.test_offer2 = OfferFactory.create(contractor=self.contractor_user, task=self.test_task2, accepted=False)

        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up method after all view tests
        """
        Skill.objects.all().delete()
        Task.objects.all().delete()

        User.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def tearDown(self):
        """
        Clean up method after each test
        """
        Offer.objects.all().delete()
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
        self.assertTemplateUsed(self.response, TestModeratorOfferListView.template)

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestModeratorOfferListView.template)
        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_offer2, self.test_offer1],
        )

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test whether the view paginates the results when there are more than ten items.
        """
        for _ in range(11):
            OfferFactory.create(contractor=self.contractor_user, task=self.test_task1)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

    def test_should_redirect_if_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page if a not-logged-in user attempts to access it.
        """
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, f"/users/accounts/login/?next={self.url}")

    def test_elements_should_be_sorted_by_id_from_newest(self):
        """
        Test whether the returned offers are sorted by id from newest.
        """
        self.assertEqual(list(self.response.context["object_list"])[0], self.test_offer2)

    def test_should_return_form_on_get(self):
        form = self.response.context.get("form")
        self.assertIsNotNone(form)

    def test_should_return_offers_filtered_by_task_title_when_query_posted(self):
        response = self.client.post(
            self.url,
            {
                "query": self.test_task1.title,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_offer1])

    def test_should_return_offers_filtered_by_task_description_when_query_posted(self):
        response = self.client.post(
            self.url,
            {
                "query": self.test_task1.description[:10],
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_offer1])

    def test_should_return_offers_filtered_by_offer_description_when_query_posted(self):
        response = self.client.post(
            self.url,
            {
                "query": self.test_offer1.description[:10],
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_offer1])

    def test_should_return_offers_filtered_by_accepted_status_on_post(self):
        """
        Test if response contains only offers with accepted status = True
        """
        self.test_offer1.accepted = True
        self.test_offer1.save()
        response = self.client.post(
            self.url,
            {
                "accepted": True,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_offer1])

    def test_should_return_offers_filtered_by_not_accepted_status_on_post(self):
        """
        Test if response contains only offers with accepted status = False
        """
        self.test_offer1.accepted = True
        self.test_offer1.save()
        response = self.client.post(
            self.url,
            {
                "accepted": False,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_offer2])

    def test_should_redirect_if_user_is_not_allowed(self):
        """
        Test if the client will be redirected if the current user is not in allowed group.
        """

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("dashboard"))


class TestModeratorOfferDetailView(TestCase):
    """
    Test case for the moderator's Offer Detail View
    """

    url_name = "offer-moderator-detail"
    template = "tasksapp/offer_detail_moderator.html"

    @classmethod
    def setUpTestData(cls):
        """
        Set up data for the whole TestCase
        """
        super().setUpTestData()
        cls.user = UserFactory.create()
        moderator_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("MODERATOR"))
        cls.user.groups.add(moderator_group)
        cls.contractor_user = UserFactory.create()
        cls.client_user = UserFactory.create()
        cls.another_user = UserFactory.create()
        cls.test_task = TaskFactory.create(client=cls.client_user)
        cls.test_offer = OfferFactory.create(contractor=cls.contractor_user, task=cls.test_task)

        cls.url = reverse(TestModeratorOfferDetailView.url_name, kwargs={"pk": cls.test_offer.id})

    @classmethod
    def tearDownClass(cls) -> None:
        Task.objects.all().delete()
        Offer.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    def test_should_retrieve_offer_detail_with_valid_offer_id(self):
        """
        Test case to check if Offer Detail View works correctly with a valid task id
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestModeratorOfferDetailView.template)
        self.assertIn("object", self.response.context)
        self.assertEqual(self.response.context["object"], self.test_offer)

    def test_should_require_login_for_offer_detail(self):
        """
        Test case to check if Offer Detail View requires user login
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")

    def test_should_redirect_if_user_is_not_allowed(self):
        """
        Test if the client will be redirected if the current user is not in allowed group.
        """
        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("dashboard"))


class TestModeratorOfferEditView(TestCase):
    """
    Test case for the contractor's edit view.
    """

    url_name = "offer-moderator-edit"
    template = "tasksapp/offer_form.html"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = UserFactory.create()
        moderator_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("MODERATOR"))
        cls.user.groups.add(moderator_group)
        cls.contractor_user = UserFactory.create()
        cls.client_user = UserFactory.create()
        cls.test_task = TaskFactory.create(client=cls.client_user)

    def setUp(self) -> None:
        super().setUp()
        self.test_offer = OfferFactory.create(contractor=self.contractor_user, task=self.test_task)
        self.client.login(username=self.user.username, password="secret")
        self.url = reverse(TestModeratorOfferEditView.url_name, kwargs={"pk": self.test_offer.id})
        self.data = {
            "description": "New offer 7620192",
        }

    @classmethod
    def tearDownClass(cls):
        Task.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Offer.objects.all().delete()
        super().tearDown()

    def test_should_return_status_code_200_when_request_is_sent(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a GET request is made.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_should_update_offer_object(self):
        """
        Test if the offer is correctly updated on post. Offer data must be updated and view redirects to detail view.
        """
        response = self.client.post(self.url, data=self.data, follow=True)

        self.assertRedirects(response, reverse("offer-moderator-detail", kwargs={"pk": self.test_offer.pk}))
        self.test_offer.refresh_from_db()
        self.assertEqual(self.test_offer.description, self.data["description"])

    def test_should_return_non_context_when_no_user_is_log_in(self):
        """
        Test whether the view correctly redirects to the login page when a non-logged-in user attempts to access it.
        """
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f"/users/accounts/login/?next={self.url}")

    def test_should_redirect_if_user_is_not_in_allowed_group(self):
        """
        Test if the client will be redirected if the current user is not in allowed group.
        """

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse("dashboard"))
