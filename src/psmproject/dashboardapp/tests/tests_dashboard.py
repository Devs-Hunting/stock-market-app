import datetime
from typing import List, Tuple

from chatapp.models import Chat, TaskChat
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone
from factories.factories import (
    ComplaintFactory,
    MessageFactory,
    OfferFactory,
    TaskFactory,
    UserFactory,
)
from mock import patch
from tasksapp.models import Complaint, Offer, Task

client = Client()


class TestBaseDashboardView(TestCase):
    @staticmethod
    def create_messages_in_order(messages: List[Tuple[Chat, User]], start_time: datetime.datetime):
        patch_now = start_time
        message_objects = []
        for message in messages:
            chat, author = message
            patch_now = patch_now + datetime.timedelta(seconds=1)
            with patch.object(timezone, "now", return_value=patch_now):
                message_objects.append(MessageFactory(chat=chat, author=author))
        return message_objects

    @classmethod
    def setUpClass(cls) -> None:
        """
        Set up method that is run once for test case. It prepares users, tasks for tests
        """
        super().setUpClass()

        cls.user1 = UserFactory.create()
        cls.user2 = UserFactory.create()
        cls.user3 = UserFactory.create()

        cls.contractor_user = UserFactory.create()
        cls.client_user = UserFactory.create()

        on_going = Task.TaskStatus.ON_GOING
        objections = Task.TaskStatus.OBJECTIONS

        start_time = datetime.datetime(2023, 1, 1, 10, 00, 00, tzinfo=datetime.timezone.utc)
        patch_now = start_time
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_task1 = TaskFactory.create(client=cls.user1, status=on_going)
            cls.test_task2 = TaskFactory.create(client=cls.user1, status=on_going)
            cls.test_task3 = TaskFactory.create(client=cls.user1, status=on_going)
            cls.test_task4 = TaskFactory.create(client=cls.user1, status=Task.TaskStatus.OPEN)
            cls.test_task5 = TaskFactory.create(client=cls.user1, status=Task.TaskStatus.ON_HOLD)
            cls.test_task6 = TaskFactory.create(client=cls.user1, status=objections)
            cls.test_task7 = TaskFactory.create(client=cls.user1, status=objections)
            cls.test_task8 = TaskFactory.create(client=cls.user1, status=Task.TaskStatus.COMPLETED)
            cls.test_task9 = TaskFactory.create(client=cls.user1, status=Task.TaskStatus.CANCELLED)

        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_task41 = TaskFactory.create(client=cls.user1, title="title41")
        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_task42 = TaskFactory.create(client=cls.user1, title="title42")
        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_task43 = TaskFactory.create(client=cls.user1, title="title43")
        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_task44 = TaskFactory.create(client=cls.user1, title="title44")
        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_task45 = TaskFactory.create(client=cls.user1, title="title45")

        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_offer1 = OfferFactory.create(contractor=cls.user2, task=cls.test_task1, accepted=True)
            cls.test_offer11 = OfferFactory.create(contractor=cls.user3, task=cls.test_task1)
            cls.test_task1.selected_offer = cls.test_offer1
            cls.test_task1.save()

        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_offer2 = OfferFactory.create(contractor=cls.user2, task=cls.test_task2, accepted=True)
            cls.test_offer21 = OfferFactory.create(contractor=cls.user3, task=cls.test_task2)
            cls.test_task2.selected_offer = cls.test_offer2
            cls.test_task2.save()

        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_offer3 = OfferFactory.create(contractor=cls.user3, task=cls.test_task3, accepted=True)
            cls.test_offer31 = OfferFactory.create(contractor=cls.user2, task=cls.test_task3)
            cls.test_task3.selected_offer = cls.test_offer3
            cls.test_task3.save()

        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_offer4 = OfferFactory.create(contractor=cls.user2, task=cls.test_task4)

        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_offer5 = OfferFactory.create(contractor=cls.user2, task=cls.test_task5)

        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_offer6 = OfferFactory.create(contractor=cls.user2, task=cls.test_task6, accepted=True)
            cls.test_task6.selected_offer = cls.test_offer6
            cls.test_task6.save()
            cls.test_complaint6 = ComplaintFactory.create(complainant=cls.user1, task=cls.test_task6)

        patch_now = patch_now + datetime.timedelta(seconds=1)
        with patch.object(timezone, "now", return_value=patch_now):
            cls.test_offer7 = OfferFactory.create(contractor=cls.user2, task=cls.test_task7, accepted=True)
            cls.test_task7.selected_offer = cls.test_offer7
            cls.test_task7.save()
            cls.test_complaint7 = ComplaintFactory.create(complainant=cls.user2, task=cls.test_task7)

        chat1 = TaskChat.objects.get(object_id=cls.test_task1.id)
        chat2 = TaskChat.objects.get(object_id=cls.test_task2.id)
        chat3 = TaskChat.objects.get(object_id=cls.test_task3.id)

        messages_definition = [
            (chat1, cls.user2),
            (chat1, cls.user1),
            (chat2, cls.user2),
            (chat2, cls.user1),
            (chat3, cls.user3),
            (chat3, cls.user1),
            (chat1, cls.user2),
            (chat1, cls.user1),
            (chat1, cls.user2),
            (chat1, cls.user1),
            (chat2, cls.user2),
            (chat2, cls.user1),
            (chat3, cls.user3),
            (chat3, cls.user1),
            (chat1, cls.user2),
            (chat1, cls.user1),
        ]
        patch_now = patch_now + datetime.timedelta(seconds=1)
        cls.messages = TestDashboardView.create_messages_in_order(messages_definition, patch_now)

    @classmethod
    def tearDownClass(cls):
        """
        Clean up method after all view tests
        """
        Complaint.objects.all().delete()
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


class TestDashboardView(TestBaseDashboardView):
    """
    Test case for the users dashboard view
    """

    url_name = "dashboard"
    template = "dashboardapp/dashboard.html"

    def setUp(self):
        self.url = reverse(TestDashboardView.url_name)

    def test_should_return_status_code_200_when_request_by_name(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a request is made.
        """
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

    def test_should_check_that_view_use_correct_template(self):
        """
        Test whether the view uses the correct template.
        """
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestDashboardView.template)

    def test_should_return_tasks(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.client.login(username=self.user1.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(
            list(self.response.context["tasks"]),
            [self.test_task3, self.test_task2, self.test_task1],
        )

    def test_should_return_new_tasks(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.client.login(username=self.user1.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(
            list(self.response.context["new_tasks"]),
            [self.test_task45, self.test_task44, self.test_task43, self.test_task42, self.test_task41],
        )

    def test_should_return_problematic_tasks(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.client.login(username=self.user1.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(
            list(self.response.context["problematic_tasks"]),
            [self.test_task7, self.test_task6],
        )

    def test_should_return_correct_latest_messages(self):
        """
        Test that only correct and latest messages are returned
        """
        self.client.login(username=self.user1.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(
            list([message.id for message in self.response.context["new_messages"]]),
            [
                self.messages[14].id,
                self.messages[12].id,
                self.messages[10].id,
                self.messages[8].id,
                self.messages[6].id,
            ],
        )

        self.client.login(username=self.user2.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(
            list([message.id for message in self.response.context["new_messages"]]),
            [self.messages[15].id, self.messages[11].id, self.messages[9].id, self.messages[7].id, self.messages[3].id],
        )

        self.client.login(username=self.user3.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(
            list([message.id for message in self.response.context["new_messages"]]),
            [self.messages[13].id, self.messages[5].id],
        )

    def test_should_not_return_objects_that_not_belong_to_the_user(self):
        """
        Test that only correct objects are returned when a request is sent to the view.
        """
        self.client.login(username=self.user1.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(list(self.response.context["jobs"]), [])
        self.assertEqual(list(self.response.context["problematic_jobs"]), [])
        self.assertEqual(list(self.response.context["new_offers"]), [])
        self.assertEqual(list(self.response.context["lost_offers"]), [])

    def test_should_return_jobs(self):
        """
        Test that only correct objects are returned when a request is sent to the view.
        """
        self.client.login(username=self.user2.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(list(self.response.context["jobs"]), [self.test_task2, self.test_task1])

        self.client.login(username=self.user3.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(list(self.response.context["jobs"]), [self.test_task3])

    def test_should_return_problematic_jobs(self):
        """
        Test that only correct objects are returned when a request is sent to the view.
        """
        self.client.login(username=self.user2.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(list(self.response.context["problematic_jobs"]), [self.test_task7, self.test_task6])

    def test_should_return_new_offers(self):
        """
        Test that only correct objects are returned when a request is sent to the view.
        """
        self.client.login(username=self.user2.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(list(self.response.context["new_offers"]), [self.test_offer5, self.test_offer4])

    def test_should_return_lost_offers(self):
        """
        Test that only correct objects are returned when a request is sent to the view.
        """
        self.client.login(username=self.user2.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(list(self.response.context["lost_offers"]), [self.test_offer31])

        self.client.login(username=self.user3.username, password="secret")
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(list(self.response.context["lost_offers"]), [self.test_offer21, self.test_offer11])

    def test_should_return_no_context_if_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page if a not-logged-in user attempts to access it.
        """
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertNotIn("tasks", self.response.context)
        self.assertNotIn("new_tasks", self.response.context)
        self.assertNotIn("problematic_tasks", self.response.context)
        self.assertNotIn("jobs", self.response.context)
        self.assertNotIn("problematic_jobs", self.response.context)
        self.assertNotIn("new_offers", self.response.context)
        self.assertNotIn("lost_offers", self.response.context)
        self.assertNotIn("new_messages", self.response.context)


class TestModeratorDashboardView(TestBaseDashboardView):
    """
    Test case for the users dashboard view
    """

    url_name = "dashboard-moderator"
    template = "dashboardapp/dashboard_moderator.html"

    def setUp(self):
        self.url = reverse(TestModeratorDashboardView.url_name)
        self.moderator_user = UserFactory.create()
        moderator_group, created = Group.objects.get_or_create(name=settings.GROUP_NAMES.get("MODERATOR"))
        self.moderator_user.groups.add(moderator_group)
        self.client.force_login(self.moderator_user)

    def test_should_check_that_view_use_correct_template(self):
        """
        Test whether the view uses the correct template.
        """
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, TestModeratorDashboardView.template)

    def test_should_return_tasks(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(
            list(self.response.context["tasks"]),
            [self.test_task3, self.test_task2, self.test_task1],
        )

    def test_should_return_new_tasks(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(
            list(self.response.context["new_tasks"]),
            [
                self.test_task45,
                self.test_task44,
                self.test_task43,
                self.test_task42,
                self.test_task41,
                self.test_task4,
                self.test_task5,
            ],
        )

    def test_should_return_problematic_tasks(self):
        """
        Test whether the correct objects are returned when a request is sent to the view.
        """
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(
            list(self.response.context["problematic_tasks"]),
            [self.test_task7, self.test_task6],
        )

    def test_should_return_correct_latest_messages(self):
        """
        Test that only correct and latest messages are returned
        """
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(
            list([message.id for message in self.response.context["new_messages"]]),
            [
                self.messages[15].id,
                self.messages[14].id,
                self.messages[13].id,
                self.messages[12].id,
                self.messages[11].id,
                self.messages[10].id,
                self.messages[9].id,
                self.messages[8].id,
                self.messages[7].id,
                self.messages[6].id,
            ],
        )

    def test_should_return_new_offers(self):
        """
        Test that only correct objects are returned when a request is sent to the view.
        """
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(
            list(self.response.context["new_offers"]),
            [
                self.test_offer5,
                self.test_offer4,
                self.test_offer31,
                self.test_offer21,
                self.test_offer11,
            ],
        )

    def test_should_return_no_context_if_not_logged_in(self):
        """
        Test whether the view correctly redirects to the login page if a not-logged-in user attempts to access it.
        """
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.context, None)

    def test_should_return_new_solutions(self):
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

        self.assertEqual(list(self.response.context["new_solutions"]), [])
