from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from factories.factories import OfferFactory, TaskFactory, UserFactory
from offerapp.models import Offer
from tasksapp.models import Task
from usersapp.models import Skill

client = Client()


class TestModeratorOfferListView(TestCase):
    """
    Test case for the moderator offers' list view
    """

    url_name = "offer-moderator-list"
    template = "offerapp/offers_list_moderator.html"

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
    template = "offerapp/offer_detail_moderator.html"

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
    template = "offerapp/offer_form.html"

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
