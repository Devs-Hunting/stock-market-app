import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from factories.factories import ComplaintFactory, OfferFactory, TaskFactory, UserFactory
from mock import patch
from tasksapp.models import Complaint, Offer, Task

client = Client()


class TestComplaintListView(TestCase):
    """
    Test case for the arbiter complaints list view
    """

    url_name = "complaint-arbiter-list"
    template = "tasksapp/complaints_list_arbiter.html"

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up method that is run once for test case. It prepares users, tasks for tests
        """
        super().setUpClass()

        cls.user = UserFactory.create()
        arbiter_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("ARBITER"))
        cls.user.groups.add(arbiter_group)
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
        cls.test_offer2 = OfferFactory.create(contractor=cls.contractor_user, task=cls.test_task2, accepted=True)
        cls.url = reverse(TestComplaintListView.url_name)

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test. It prepares complaints, logs in arbiter and gets view
        response
        """
        super().setUp()

        self.test_complaint1 = ComplaintFactory.create(complainant=self.client_user, task=self.test_task1)
        self.test_complaint2 = ComplaintFactory.create(complainant=self.client_user, task=self.test_task2)

        self.client.login(username=self.user.username, password="secret")
        self.response = self.client.get(self.url)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up method after all view tests
        """
        Offer.objects.all().delete()
        Task.objects.all().delete()
        User.objects.all().delete()
        Group.objects.all().delete()
        super().tearDownClass()

    def tearDown(self):
        """
        Clean up method after each test
        """
        Complaint.objects.all().delete()
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
        self.assertTemplateUsed(self.response, TestComplaintListView.template)

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestComplaintListView.template)
        self.assertEqual(
            list(self.response.context["object_list"]),
            [self.test_complaint2, self.test_complaint1],
        )

    def test_should_make_pagination_if_there_is_more_then_ten_element(self):
        """
        Test whether the view paginates the results when there are more than ten items.
        """
        temp_tasks = []
        for _ in range(11):
            temp_task = TaskFactory.create(client=self.client_user)
            temp_tasks.append(temp_task)
            ComplaintFactory.create(complainant=self.contractor_user, task=temp_task)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="?page=2"')
        self.assertEqual(len(response.context["object_list"]), 10)

        for task in temp_tasks:
            task.delete()

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
        self.assertEqual(list(self.response.context["object_list"])[0], self.test_complaint2)

    def test_should_return_form_on_get(self):
        form = self.response.context.get("form")
        self.assertIsNotNone(form)

    def test_should_return_offers_filtered_by_task_title_when_query_sent(self):
        response = self.client.get(
            self.url,
            {
                "query": self.test_task1.title,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_complaint1])

    def test_should_return_offers_filtered_by_task_description_when_query_sent(self):
        response = self.client.get(
            self.url,
            {
                "query": self.test_task1.description[:10],
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_complaint1])

    def test_should_return_offers_filtered_by_complaint_content_when_query_sent(self):
        response = self.client.get(
            self.url,
            {
                "query": self.test_complaint1.content[:10],
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_complaint1])

    def test_should_return_complaints_filtered_by_taken_by_arbiter_status(self):
        """
        Test if response contains only complaints that have arbiter assigned
        """
        self.test_complaint1.arbiter = self.user
        self.test_complaint1.save()
        response = self.client.get(
            self.url,
            {
                "taken": True,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_complaint1])

    def test_should_return_complaints_filtered_by_closed_status(self):
        """
        Test if response contains only complaints that are closed
        """
        self.test_complaint1.closed = True
        self.test_complaint1.save()
        response = self.client.get(
            self.url,
            {
                "closed": True,
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [self.test_complaint1])

    def test_should_return_complaints_filtered_by_start_date(self):
        """
        Test if response contains only complaints that are changed after given date
        """
        self.test_complaint1.closed = True
        self.test_complaint1.save()
        future_date = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=10)
        start_date = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=5)

        # create complaint "in the future"
        with patch.object(timezone, "now", return_value=future_date):
            temp_complaint = ComplaintFactory.create(complainant=self.contractor_user, task=self.test_task1)

        response = self.client.get(
            self.url,
            {
                "date_start": start_date.strftime("%Y-%m-%d"),
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [temp_complaint])

    def test_should_return_complaints_filtered_by_end_date(self):
        """
        Test if response contains only complaints that are changed before given date
        """
        self.test_complaint1.closed = True
        self.test_complaint1.save()
        past_date = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=10)
        end_date = datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(days=5)

        # create complaint "in the future"
        with patch.object(timezone, "now", return_value=past_date):
            temp_complaint = ComplaintFactory.create(complainant=self.contractor_user, task=self.test_task1)

        response = self.client.get(
            self.url,
            {
                "date_end": end_date.strftime("%Y-%m-%d"),
            },
        )
        self.assertQuerysetEqual(response.context["object_list"], [temp_complaint])

    def test_should_redirect_if_user_is_not_allowed(self):
        """
        Test if the client will be redirected if the current user is not in allowed group.
        """

        another_user = UserFactory.create()
        self.client.login(username=another_user.username, password="secret")
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse("dashboard"))
