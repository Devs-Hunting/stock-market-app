from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import Group
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.timezone import now
from factories.factories import UserFactory
from usersapp.models import BlockedUser

client = Client()


class TestBlockUserView(TestCase):
    """
    Test case for the block user view.
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test.
        """
        super().setUp()
        self.user = UserFactory.create()
        self.administrator = UserFactory.create()
        self.administrator.groups.add(Group.objects.get(name=settings.GROUP_NAMES.get("ADMINISTRATOR")))
        self.client.force_login(self.administrator)
        blocking_end_date = now() + timedelta(days=4)
        self.blocked_user_data = {
            "blocked_user": self.user.id,
            "reason": "test",
            "blocking_end_date": blocking_end_date,
        }

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        super().tearDown()

    def test_should_return_status_code_200_when_request(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a request is made.
        """
        response = self.client.get(reverse("block-user"))

        self.assertEqual(response.status_code, 200)

    def test_should_add_user_to_group_blocked_user(self):
        """
        Test whether the user is added to the group of blocked users when a request is made.
        """
        self.client.post(reverse("block-user"), data=self.blocked_user_data, follow=True)

        self.assertTrue(self.user.groups.filter(name=settings.GROUP_NAMES.get("BLOCKED_USER")).exists())

    def test_should_add_record_about_blocked_user_with_proper_attributes(self):
        """
        Test whether the user is added record about blocked user when a request is made.
        """
        self.client.post(reverse("block-user"), data=self.blocked_user_data, follow=True)
        blocked_user = BlockedUser.objects.get(blocked_user=self.user)

        self.assertTrue(blocked_user.blocked_user == self.user)
        self.assertEqual(blocked_user.reason, self.blocked_user_data["reason"])
        self.assertEqual(blocked_user.blocking_end_date, self.blocked_user_data["blocking_end_date"])

    def test_should_not_allow_when_normal_user_try_block_user(self):
        """
        Test whether the normal user can't block another user.
        """
        self.client.force_login(self.user)
        response = self.client.post(reverse("block-user"), data=self.blocked_user_data, follow=True)

        self.assertRedirects(response, reverse("dashboard"))
        self.assertFalse(self.user.groups.filter(name=settings.GROUP_NAMES.get("BLOCKED_USER")).exists())

    def test_should_permanently_block_user_and_set_is_active_to_false(self):
        """
        Test whether the user is blocked permanently when a request is made.
        """
        full_blocked_user = UserFactory.create()
        full_blocked_user_data = {
            "blocked_user": full_blocked_user.id,
            "reason": "test2",
            "full_blocking": True,
        }
        self.client.post(reverse("block-user"), data=full_blocked_user_data, follow=True)
        full_blocked_user.refresh_from_db()

        self.assertTrue(full_blocked_user.groups.filter(name=settings.GROUP_NAMES.get("BLOCKED_USER")).exists())
        self.assertFalse(full_blocked_user.is_active)


class TestBlockUserDetailView(TestCase):
    """
    Test case for the block user detail view.
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test.
        """
        super().setUp()
        self.user = UserFactory.create()
        self.administrator = UserFactory.create()
        self.administrator.groups.add(Group.objects.get(name=settings.GROUP_NAMES.get("ADMINISTRATOR")))
        self.client.force_login(self.administrator)
        self.blocked_user = BlockedUser.objects.create(
            blocked_user=self.user,
            reason="test",
            blocking_end_date=now() + timedelta(days=4),
            blocking_user=self.administrator,
        )

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        super().tearDown()

    def test_should_retrieve_blocked_user_detail_with_valid_id(self):
        """
        Test case to check if blocked user detail is retrieved with valid id
        """
        response = self.client.get(reverse("blocked-user-detail", kwargs={"pk": self.blocked_user.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usersapp/block_user_detail.html")
        self.assertEqual(response.context["object"], self.blocked_user)

    def test_should_redirect_for_blocked_user_detail_access_by_standard_user(self):
        """
        Test case to check if Blocked User Detail View requires special user to access.
        """
        self.client.force_login(self.user)
        response = self.client.get(reverse("blocked-user-detail", kwargs={"pk": self.blocked_user.id}))

        self.assertRedirects(response, reverse("dashboard"))


class TestBlockUserListView(TestCase):
    """
    Test case for the block user list view.
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test.
        """
        super().setUp()
        self.user = UserFactory.create()
        self.user2 = UserFactory.create()
        self.administrator = UserFactory.create()
        self.administrator.groups.add(Group.objects.get(name=settings.GROUP_NAMES.get("ADMINISTRATOR")))
        self.client.force_login(self.administrator)
        self.blocked_user = BlockedUser.objects.create(
            blocked_user=self.user,
            reason="reason of blocking",
            blocking_end_date=now() + timedelta(days=4),
            blocking_user=self.administrator,
        )
        self.blocked_user2 = BlockedUser.objects.create(
            blocked_user=self.user2,
            reason="test2",
            blocking_end_date=now() + timedelta(days=2),
            blocking_user=self.administrator,
        )

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        super().tearDown()

    def test_should_return_status_code_200_when_request(self):
        """
        Test whether the view returns a HTTP 200 OK status code when a request is made.
        """
        response = self.client.get(reverse("blocked-users-list"))

        self.assertEqual(response.status_code, 200)

    def test_should_return_correct_template(self):
        """
        Test whether the view returns the correct template when a request is made.
        """
        response = self.client.get(reverse("blocked-users-list"))

        self.assertTemplateUsed(response, "usersapp/blocked_users_list.html")

    def test_should_return_correct_objects_when_request_is_sent(self):
        """
        Test whether the view returns the correct objects when a request is made.
        """
        response = self.client.get(reverse("blocked-users-list"))

        self.assertEqual(len(response.context["object_list"]), 2)
        self.assertEqual(response.context["object_list"][0], self.blocked_user2)

    def test_elements_should_be_sorted_by_id_from_newest(self):
        """
        Test whether the elements in the list are sorted from newest to oldest.
        """
        response = self.client.get(reverse("blocked-users-list"))

        self.assertEqual(response.context["object_list"][0], self.blocked_user2)

    def test_should_return_objects_filtered_by_phrases_in_username(self):
        """
        Test whether the view returns the correct objects when a request is made.
        """
        response = self.client.get(reverse("blocked-users-list"), data={"q": self.user.username})

        self.assertEqual(len(response.context["object_list"]), 1)
        self.assertEqual(response.context["object_list"][0], self.blocked_user)

    def test_should_return_objects_filtered_by_phrases_in_reason_for_blocked_user(self):
        """
        Test whether the view returns the correct objects when a request is made.
        """
        response = self.client.get(reverse("blocked-users-list"), data={"q": self.blocked_user.reason})

        self.assertEqual(len(response.context["object_list"]), 1)
        self.assertEqual(response.context["object_list"][0], self.blocked_user)


class TestUnblockUserView(TestCase):
    """
    Test case for the unblock user view.
    """

    def setUp(self) -> None:
        """
        Set up method that is run before every individual test.
        """
        super().setUp()
        self.user = UserFactory.create()
        self.administrator = UserFactory.create()
        self.administrator.groups.add(Group.objects.get(name=settings.GROUP_NAMES.get("ADMINISTRATOR")))
        self.client.force_login(self.administrator)
        self.blocked_user = BlockedUser.objects.create(
            blocked_user=self.user,
            reason="test",
            blocking_end_date=now() + timedelta(days=4),
            blocking_user=self.administrator,
        )

    def tearDown(self):
        """
        Clean up method after each test case.
        """
        super().tearDown()

    def test_should_remove_blocked_user_from_group_blocked_users(self):
        """
        Test whether the view removes the blocked user from the group blocked_users when a request is made.
        """
        self.client.post(reverse("unblock-user", kwargs={"pk": self.blocked_user.id}))
        self.assertFalse(self.user.groups.filter(name=settings.GROUP_NAMES.get("BLOCKED_USER")).exists())

    def test_should_set_date_for_blocking_end_date_to_now(self):
        """
        Test whether the view sets the date for blocking end date to now when a request is made.
        """
        self.client.post(reverse("unblock-user", kwargs={"pk": self.blocked_user.id}), follow=True)
        self.blocked_user.refresh_from_db()

        self.assertEqual(self.blocked_user.blocking_end_date.strftime("%Y-%m-%d"), now().strftime("%Y-%m-%d"))

    def test_should_redirect_to_dashboard_when_normal_user_wants_to_unblock_user(self):
        """
        Test whether the view redirects to dashboard when a normal user wants to unblock a user.
        """
        user2 = UserFactory.create()
        self.client.force_login(user2)
        response = self.client.post(reverse("unblock-user", kwargs={"pk": self.blocked_user.id}))

        self.assertRedirects(response, reverse("dashboard"))
