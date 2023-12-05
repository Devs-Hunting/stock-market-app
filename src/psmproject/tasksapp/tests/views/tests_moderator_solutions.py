import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from factories.factories import OfferFactory, SolutionFactory, TaskFactory, UserFactory
from mock import patch
from tasksapp.models import Offer, Solution, Task
from usersapp.models import Skill

client = Client()


class TestModeratorSolutionListView(TestCase):
    """
    Test case for the moderator solutions' list view
    """

    url_name = "solutions-moderator-list"
    template = "tasksapp/solutions_list_moderator.html"

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
        cls.test_offer1 = OfferFactory.create(contractor=cls.contractor_user, task=cls.test_task1, accepted=True)
        cls.test_task1.selected_offer = cls.test_offer1
        cls.test_task1.save()
        cls.test_offer2 = OfferFactory.create(contractor=cls.contractor_user, task=cls.test_task2, accepted=True)
        cls.test_task2.selected_offer = cls.test_offer2
        cls.test_task2.save()
        cls.url = reverse(TestModeratorSolutionListView.url_name)

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. It prepares offers, logs in moderator and gets view
        response
        """
        super().setUp()
        self.test_solution1 = SolutionFactory.create()
        self.test_offer1.solution = self.test_solution1
        self.test_offer1.save()
        self.test_solution2 = SolutionFactory.create()
        self.test_offer2.solution = self.test_solution2
        self.test_offer2.save()
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up method after all view tests
        """
        Offer.objects.all().delete()
        Task.objects.all().delete()
        Skill.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def tearDown(self):
        """
        Clean up method after each test
        """
        Solution.objects.all().delete()
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
        self.assertTemplateUsed(self.response, TestModeratorSolutionListView.template)

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestModeratorSolutionListView.template)
        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_solution2, self.test_solution1],
        )

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test whether the view paginates the results when there are more than ten items.
        """
        tasks = []
        offers = []
        for _ in range(11):
            test_task = TaskFactory.create(client=self.client_user)
            test_offer = OfferFactory.create(contractor=self.contractor_user, task=test_task, accepted=True)
            test_task.selected_offer = test_offer
            test_task.save()
            tasks.append(test_task)
            offers.append(test_offer)
            test_solution = SolutionFactory.create(offer=test_offer)
            test_offer.solution = test_solution
            test_offer.save()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

        for task in tasks:
            task.delete()
        for offer in offers:
            offer.delete()

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
        self.assertEqual(list(self.response.context["object_list"])[0], self.test_solution2)

    def test_should_return_form_on_get(self):
        form = self.response.context.get("form")
        self.assertIsNotNone(form)

    def test_should_return_solutions_filtered_by_task_title_when_query_sent(self):
        response = self.client.get(
            self.url,
            {
                "query": self.test_task1.title,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_solution1])

    def test_should_return_solutions_filtered_by_task_description_when_query_sent(self):
        response = self.client.get(
            self.url,
            {
                "query": self.test_task1.description[:10],
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_solution1])

    def test_should_return_solutions_filtered_by_solution_description_when_query_sent(self):
        response = self.client.get(
            self.url,
            {
                "query": self.test_solution1.description[:10],
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_solution1])

    def test_should_return_solutions_filtered_by_accepted_status(self):
        """
        Test if response contains only offers with accepted status = True
        """
        self.test_solution1.accepted = True
        self.test_solution1.save()
        response = self.client.get(
            self.url,
            {
                "accepted": True,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_solution1])

    def test_should_return_solution_filtered_by_not_accepted_status(self):
        """
        Test if response contains only offers with accepted status = False
        """
        self.test_solution1.accepted = True
        self.test_solution1.save()
        response = self.client.get(
            self.url,
            {
                "accepted": False,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_solution2])

    def test_should_redirect_if_user_is_not_allowed(self):
        """
        Test if the client will be redirected if the current user is not in allowed group.
        """

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("dashboard"))


class TestModeratorSolutionNewListView(TestCase):
    """
    Test case for the moderator newest solutions' list view
    """

    url_name = "solutions-moderator-list-new"
    template = "tasksapp/solutions_list_moderator.html"

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up method that is run once for test case. It prepares skills, users, tasks for tests
        """
        super().setUpClass()
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
        cls.test_task3 = TaskFactory.create(
            client=cls.client_user,
            title="UniqueTitle3",
        )
        cls.test_offer1 = OfferFactory.create(contractor=cls.contractor_user, task=cls.test_task1, accepted=True)
        cls.test_task1.selected_offer = cls.test_offer1
        cls.test_task1.save()
        cls.test_offer2 = OfferFactory.create(contractor=cls.contractor_user, task=cls.test_task2, accepted=True)
        cls.test_task2.selected_offer = cls.test_offer2
        cls.test_task2.save()
        cls.test_offer3 = OfferFactory.create(contractor=cls.contractor_user, task=cls.test_task3, accepted=True)
        cls.test_task3.selected_offer = cls.test_offer3
        cls.test_task3.save()
        cls.url = reverse(TestModeratorSolutionNewListView.url_name)

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. It prepares offers, logs in moderator and gets view
        response
        """
        super().setUp()

        self.test_solution1 = SolutionFactory.create(offer=self.test_offer1)
        self.test_solution2 = SolutionFactory.create(offer=self.test_offer2)

        # create very old solution that should not be on the list
        with patch.object(timezone, "now", return_value=datetime.datetime(2023, 1, 1, tzinfo=datetime.timezone.utc)):
            self.test_solution3 = SolutionFactory.create(offer=self.test_offer3)

        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up method after all view tests
        """
        Skill.objects.all().delete()
        Offer.objects.all().delete()
        Task.objects.all().delete()

        User.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def tearDown(self):
        """
        Clean up method after each test
        """
        Solution.objects.all().delete()
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
        self.assertTemplateUsed(self.response, TestModeratorSolutionListView.template)

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestModeratorSolutionListView.template)
        self.response = self.client.get(self.url)
        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_solution2, self.test_solution1],
        )

    def test_elements_should_be_sorted_by_id_from_newest(self):
        """
        Test whether the returned offers are sorted by id from newest.
        """
        self.assertEqual(list(self.response.context["object_list"])[0], self.test_solution2)

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test whether the view paginates the results when there are more than ten items.
        """
        tasks = []
        offers = []
        for _ in range(11):
            test_task = TaskFactory.create(client=self.client_user)
            test_offer = OfferFactory.create(contractor=self.contractor_user, task=test_task, accepted=True)
            test_task.selected_offer = test_offer
            test_task.save()
            tasks.append(test_task)
            offers.append(test_offer)
            SolutionFactory.create(offer=test_offer)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

        for task in tasks:
            task.delete()
        for offer in offers:
            offer.delete()

    def test_should_redirect_if_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page if a not-logged-in user attempts to access it.
        """
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, f"/users/accounts/login/?next={self.url}")

    def test_should_redirect_if_user_is_not_allowed(self):
        """
        Test if the client will be redirected if the current user is not in allowed group.
        """

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("dashboard"))


class TestModeratorSolutionDetailView(TestCase):
    """
    Test case for the moderator's Solution Detail View
    """

    url_name = "solution-moderator-detail"
    template = "tasksapp/solution_detail_moderator.html"

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
        cls.test_offer = OfferFactory.create(contractor=cls.contractor_user, task=cls.test_task, accepted=True)
        cls.test_task.selected_offer = cls.test_offer
        cls.test_solution = SolutionFactory.create(offer=cls.test_offer)
        cls.url = reverse(TestModeratorSolutionDetailView.url_name, kwargs={"pk": cls.test_solution.id})

    @classmethod
    def tearDownClass(cls) -> None:
        Solution.objects.all().delete()
        Offer.objects.all().delete()
        Task.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def setUp(self) -> None:
        super().setUp()
        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    def test_should_retrieve_solution_detail_with_valid_solution_id(self):
        """
        Test case to check if Solution Detail View works correctly with a valid task id
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestModeratorSolutionDetailView.template)
        self.assertIn("object", self.response.context)
        self.assertEqual(self.response.context["object"], self.test_solution)

    def test_should_require_login_for_solution_detail(self):
        """
        Test case to check if Solution Detail View requires user login
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


class TestModeratorSolutionEditView(TestCase):
    """
    Test case for the moderator's edit view.
    """

    url_name = "solution-moderator-edit"
    template = "tasksapp/solution_form.html"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = UserFactory.create()
        moderator_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("MODERATOR"))
        cls.user.groups.add(moderator_group)
        cls.contractor_user = UserFactory.create()
        cls.client_user = UserFactory.create()
        cls.test_task = TaskFactory.create(client=cls.client_user)
        cls.test_offer = OfferFactory.create(contractor=cls.contractor_user, task=cls.test_task)
        cls.test_task.selected_offer = cls.test_offer
        cls.test_task.save()

    def setUp(self) -> None:
        super().setUp()
        self.test_solution = SolutionFactory.create()
        self.test_offer.solution = self.test_solution
        self.test_offer.save()
        self.client.login(username=self.user.username, password="secret")
        self.url = reverse(TestModeratorSolutionEditView.url_name, kwargs={"pk": self.test_solution.id})
        self.data = {
            "description": "New solution 7620192",
        }

    @classmethod
    def tearDownClass(cls):
        Offer.objects.all().delete()
        Task.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        Solution.objects.all().delete()
        super().tearDown()

    def test_should_return_status_code_200_when_request_is_sent(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a GET request is made.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_should_update_solution_object(self):
        """
        Test if the solution is correctly updated on post. Solution data must be updated and view redirects to detail
        view.
        """
        response = self.client.post(self.url, data=self.data, follow=True)
        self.assertRedirects(response, reverse("solution-moderator-detail", kwargs={"pk": self.test_solution.pk}))
        self.test_solution.refresh_from_db()
        self.assertEqual(self.test_solution.description, self.data["description"])

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
