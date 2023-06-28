from django.contrib.auth.models import User
from django.test import TestCase
from usersapp.models import Notification, Rating, Skill, UserProfile


class SkillModelTestCase(TestCase):
    def test_should_create_skill_when_valid_data_provided(self):
        skill = Skill.objects.create(skill="Python")
        self.assertEqual(skill.skill, "Python")

    def test_should_have_correct_string_representation(self):
        skill = Skill.objects.create(skill="Python")
        self.assertEqual(str(skill), "Python")


class NotificationModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")

    def test_should_create_notification_when_valid_data_provided(self):
        notification = Notification.objects.create(
            user=self.user, content="New notification"
        )
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.content, "New notification")

    def test_should_have_correct_string_representation(self):
        notification = Notification.objects.create(
            user=self.user, content="New notification"
        )
        expected_string = f"Notification #{notification.id}"
        self.assertEqual(str(notification), expected_string)


class UserProfileModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")

    def test_should_create_user_profile_when_valid_data_provided(self):
        profile = UserProfile.objects.create(
            user=self.user, description="Test description"
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.description, "Test description")

    def test_should_have_correct_string_representation(self):
        profile = UserProfile.objects.create(
            user=self.user, description="Test description"
        )
        expected_string = f"Profile for {self.user.username}"
        self.assertEqual(str(profile), expected_string)


class RatingModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="testuser")

    def test_should_create_rating_when_valid_data_provided(self):
        rating = Rating.objects.create(
            user=self.user,
            code_quality=4.5,
            solution_time=3.2,
            contact=4.0,
        )
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.code_quality, 4.5)
        self.assertEqual(rating.solution_time, 3.2)
        self.assertEqual(rating.contact, 4.0)

    def test_should_have_correct_string_representation(self):
        rating = Rating.objects.create(
            user=self.user,
            code_quality=4.5,
            solution_time=3.2,
            contact=4.0,
        )
        expected_string = f"Rating for {self.user.username}"
        self.assertEqual(str(rating), expected_string)
