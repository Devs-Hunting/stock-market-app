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
    """
    A base test case that sets up a user, a skill, a notification,
    a rating and a user profile for other test cases.
    """

    def setUp(self):
        """
        Set up a user, a skill, a notification, a rating, and a user profile for use in tests.
        """
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.skill = Skill.objects.create(skill="Python")
        self.notification = Notification.objects.create(
            user=self.user, content="Test notification"
        )
        self.rating = Rating.objects.create(
            user=self.user, code_quality=4.5, solution_time=4.0, contact=4.5
        )
        self.user_profile = UserProfile.objects.create(
            user=self.user, description="Test description"
        )
        self.user_profile.skills.add(self.skill)


class SkillModelTest(BaseTestCase):
    """
    A test case for the Skill model.
    """

    def test_should_create_skill(self):
        """
        Test if the Skill instance is created correctly.
        """
        self.assertEqual(Skill.objects.count(), 1)
        self.assertEqual(self.skill.skill, "Python")


class NotificationModelTest(BaseTestCase):
    """
    A test case for the Notification model.
    """

    def test_should_create_notification(self):
        """
        Test if the Notification instance is created correctly.
        """
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(self.notification.content, "Test notification")
        self.assertEqual(self.notification.user, self.user)

    def test_notification_auto_created_at_field(self):
        """
        Verify that the created_at field is automatically filled upon instance creation.
        """
        self.assertIsNotNone(self.notification.created_at)

    def test_user_field(self):
        """
        Test if the user field is a foreign key pointing to the User model.
        """
        field = Notification._meta.get_field("user")
        self.assertIsInstance(field, models.ForeignKey)
        self.assertEqual(field.related_model, get_user_model())

    def test_content_field(self):
        """
        Test if the content field is a CharField with a maximum length of 150.
        """
        field = Notification._meta.get_field("content")
        self.assertIsInstance(field, models.CharField)
        self.assertEqual(field.max_length, 150)


class UserProfileModelTest(BaseTestCase):
    """
    A test case for the UserProfile model.
    """

    def test_should_create_user_profile(self):
        """
        Test if the UserProfile instance is created correctly.
        """
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(self.user_profile.description, "Test description")
        self.assertEqual(self.user_profile.user, self.user)
        self.assertIn(self.skill, self.user_profile.skills.all())

    def test_should_have_created_at_and_updated_at(self):
        """
        Verify that the created_at and updated_at fields are automatically filled upon instance creation and update.
        """
        self.assertIsNotNone(self.user_profile.created_at)
        self.assertIsNotNone(self.user_profile.updated_at)

    def test_user_field(self):
        """
        Test if the user field is a one-to-one field pointing to the User model.
        """
        field = UserProfile._meta.get_field("user")
        self.assertIsInstance(field, models.OneToOneField)
        self.assertEqual(field.related_model, get_user_model())

    def test_description_field(self):
        """
        Test if the description field is a TextField.
        """
        field = UserProfile._meta.get_field("description")
        self.assertIsInstance(field, models.TextField)

    def test_skills_field(self):
        """
        Test if the skills field is a ManyToManyField pointing to the Skill model.
        """
        field = UserProfile._meta.get_field("skills")
        self.assertIsInstance(field, models.ManyToManyField)
        self.assertEqual(field.related_model, Skill)


class RatingModelTest(BaseTestCase):
    """
    A test case for the Rating model.
    """

    def test_should_create_rating(self):
        """
        Test if the Rating instance is created correctly.
        """
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(self.rating.user, self.user)
        self.assertEqual(self.rating.code_quality, 4.5)
        self.assertEqual(self.rating.solution_time, 4.0)
        self.assertEqual(self.rating.contact, 4.5)

    def test_user_field(self):
        """
        Test if the user field is a one-to-one field pointing to the User model.
        """
        field = Rating._meta.get_field("user")
        self.assertIsInstance(field, models.OneToOneField)
        self.assertEqual(field.related_model, get_user_model())

    def test_code_quality_field(self):
        """
        Test if the code_quality field is a DecimalField with max_digits 2 and decimal_places 1.
        """
        field = Rating._meta.get_field("code_quality")
        self.assertIsInstance(field, models.DecimalField)
        self.assertEqual(field.max_digits, 2)
        self.assertEqual(field.decimal_places, 1)

    def test_solution_time_field(self):
        """
        Test if the solution_time field is a DecimalField with max_digits 2 and decimal_places 1.
        """
        field = Rating._meta.get_field("solution_time")
        self.assertIsInstance(field, models.DecimalField)
        self.assertEqual(field.max_digits, 2)
        self.assertEqual(field.decimal_places, 1)

    def test_contact_field(self):
        """
        Test if the contact field is a DecimalField with max_digits 2 and decimal_places 1.
        """
        field = Rating._meta.get_field("contact")
        self.assertIsInstance(field, models.DecimalField)
        self.assertEqual(field.max_digits, 2)
        self.assertEqual(field.decimal_places, 1)


class GetProfilePicturePathTest(BaseTestCase):
    """
    A test case for the get_profile_picture_path function.
    """

    def test_should_get_profile_picture_path(self):
        """
        Test if the function returns the correct path for the user's profile picture.
        """
        filename = "test.jpg"
        expected_path = f"profile_pictures/{self.user.id}/{filename}"
        self.assertEqual(
            get_profile_picture_path(self.user.profile, filename), expected_path
        )
