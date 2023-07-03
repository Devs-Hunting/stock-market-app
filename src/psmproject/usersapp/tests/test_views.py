from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import RequestFactory
from django.urls import reverse
from usersapp.views import ProfileView


class ProfileViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )

    def test_profile_view_renders_template(self):
        """
        Test that the profile view renders the correct template.
        """
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "usersapp/profile.html")

    def test_profile_view_inherits_login_required_mixin(self):
        """
        Test that the profile view inherits from LoginRequiredMixin.
        """
        self.assertTrue(issubclass(ProfileView, LoginRequiredMixin))
