from django.contrib.auth import get_user_model
from django.db import models
from django.test import TestCase
from usersapp.models import (
    Notification,
    Rating,
    Skill,
    UserProfile,
    get_profile_picture_path,
)

User = get_user_model()


class BaseTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.skill = Skill.objects.create(skill="Python")
        self.notification = Notification.objects.create(
            user=self.user, content="Test notification"
        )
        self.rating = Rating.objects.create(user=self.user, rating=5)
        self.user_profile = UserProfile.objects.create(
            user=self.user, description="Test description"
        )
        self.user_profile.skills.add(self.skill)


class SkillModelTest(TestCase):
    def setUp(self):
        self.skill = Skill.objects.create(skill="Python")

    def test_should_create_skill(self):
        self.assertEqual(Skill.objects.count(), 1)
        self.assertEqual(self.skill.skill, "Python")


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.notification = Notification.objects.create(
            user=self.user, content="Test notification"
        )

    def test_should_create_notification(self):
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(self.notification.content, "Test notification")
        self.assertEqual(self.notification.user, self.user)

    def test_should_have_created_at_auto_now_add(self):
        self.assertIsNotNone(self.notification.created_at)

    def test_user_field(self):
        field = Notification._meta.get_field("user")
        self.assertIsInstance(field, models.ForeignKey)
        self.assertEqual(field.related_model, get_user_model())

    def test_content_field(self):
        field = Notification._meta.get_field("content")
        self.assertIsInstance(field, models.CharField)
        self.assertEqual(field.max_length, 150)


class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.skill = Skill.objects.create(skill="Python")
        self.user_profile = UserProfile.objects.create(
            user=self.user, description="Test description"
        )
        self.user_profile.skills.add(self.skill)

    def test_should_create_user_profile(self):
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(self.user_profile.description, "Test description")
        self.assertEqual(self.user_profile.user, self.user)
        self.assertIn(self.skill, self.user_profile.skills.all())

    def test_should_have_created_at_and_updated_at(self):
        self.assertIsNotNone(self.user_profile.created_at)
        self.assertIsNotNone(self.user_profile.updated_at)

    def test_user_field(self):
        field = UserProfile._meta.get_field("user")
        self.assertIsInstance(field, models.OneToOneField)
        self.assertEqual(field.related_model, get_user_model())

    def test_description_field(self):
        field = UserProfile._meta.get_field("description")
        self.assertIsInstance(field, models.TextField)

    def test_skills_field(self):
        field = UserProfile._meta.get_field("skills")
        self.assertIsInstance(field, models.ManyToManyField)
        self.assertEqual(field.related_model, Skill)


class RatingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.rating = Rating.objects.create(
            user=self.user, code_quality=4.5, solution_time=4.0, contact=4.5
        )

    def test_should_create_rating(self):
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(self.rating.user, self.user)
        self.assertEqual(self.rating.code_quality, 4.5)
        self.assertEqual(self.rating.solution_time, 4.0)
        self.assertEqual(self.rating.contact, 4.5)

    def test_user_field(self):
        field = Rating._meta.get_field("user")
        self.assertIsInstance(field, models.OneToOneField)
        self.assertEqual(field.related_model, get_user_model())

    def test_code_quality_field(self):
        field = Rating._meta.get_field("code_quality")
        self.assertIsInstance(field, models.DecimalField)
        self.assertEqual(field.max_digits, 2)
        self.assertEqual(field.decimal_places, 1)

    def test_solution_time_field(self):
        field = Rating._meta.get_field("solution_time")
        self.assertIsInstance(field, models.DecimalField)
        self.assertEqual(field.max_digits, 2)
        self.assertEqual(field.decimal_places, 1)

    def test_contact_field(self):
        field = Rating._meta.get_field("contact")
        self.assertIsInstance(field, models.DecimalField)
        self.assertEqual(field.max_digits, 2)
        self.assertEqual(field.decimal_places, 1)


class GetProfilePicturePathTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.user_profile = UserProfile.objects.create(
            user=self.user, description="Test description"
        )

    def test_should_get_profile_picture_path(self):
        filename = "test.jpg"
        expected_path = f"profile_pictures/{self.user.id}/{filename}"
        self.assertEqual(
            get_profile_picture_path(self.user.profile, filename), expected_path
        )
