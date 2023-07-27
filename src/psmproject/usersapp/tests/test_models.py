from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from usersapp.models import (
    Notification,
    Rating,
    Skill,
    UserProfile,
    get_profile_picture_path,
)


class TestSkillModel(TestCase):
    """
    Test cases for the Skill model.
    """

    def setUp(self):
        self.skill_name = "Test skill"

    def test_should_increase_skill_count_and_set_correct_name_after_skill_creation(
        self,
    ):
        """
        Test that checks if creating a Skill increases the count and sets the skill name correctly.
        """
        skill = Skill.objects.create(skill=self.skill_name)
        self.assertEqual(Skill.objects.count(), 1)
        self.assertEqual(skill.skill, self.skill_name)

    def test_should_raise_validation_error_when_creating_skill_with_duplicate_name(
        self,
    ):
        """
        Test that checks if creating a Skill with a duplicate name raises a ValidationError.
        """
        Skill.objects.create(skill=self.skill_name)
        with self.assertRaisesMessage(ValidationError, "Skill with this "):
            duplicate_skill = Skill(skill=self.skill_name)
            duplicate_skill.full_clean()

    def test_should_raise_validation_error_when_creating_skill_with_name_exceeding_max_length(
        self,
    ):
        """
        Test that checks if creating a Skill with a name longer than 40 characters raises a ValidationError.
        """
        long_skill_name = "a" * 41
        with self.assertRaisesMessage(
            ValidationError,
            f"Ensure this value has at most 40 characters (it has {len(long_skill_name)}).",
        ):
            skill = Skill(skill=long_skill_name)
            skill.full_clean()


class TestNotificationModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")

    def tearDown(self):
        Notification.objects.all().delete()

    def test_should_increase_notification_count_and_set_correct_content_and_user_after_notification_creation(
        self,
    ):
        """
        Test that checks if creating a Notification increases the count and sets the content and user correctly.
        """
        content = "Test notification"
        notification = Notification.objects.create(user=self.user, content=content)
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(notification.content, content)
        self.assertEqual(notification.user, self.user)

    def test_should_raise_validation_error_when_creating_notification_with_content_exceeding_max_length(
        self,
    ):
        """
        Test that checks if creating a Notification with content longer than 150 characters raises a ValidationError.
        """
        long_content = "a" * 151
        with self.assertRaises(ValidationError):
            notification = Notification(user=self.user, content=long_content)
            notification.full_clean()

    def test_should_raise_validation_error_when_creating_notification_with_empty_content(
        self,
    ):
        """
        Test that checks if creating a Notification with empty content raises a ValidationError.
        """
        with self.assertRaises(ValidationError):
            notification = Notification(user=self.user, content="")
            notification.full_clean()


class TestUserProfileModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.skill = Skill.objects.create(skill="Test skill")

    def tearDown(self):
        UserProfile.objects.all().delete()

    def test_should_increase_user_profile_count_and_set_correct_fields_after_user_profile_creation(
        self,
    ):
        """
        Test that checks if creating a UserProfile increases the count and sets the fields correctly.
        """
        description = "Test description"
        user_profile = UserProfile.objects.create(
            user=self.user, description=description
        )
        user_profile.skills.add(self.skill)
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(user_profile.description, description)
        self.assertEqual(user_profile.skills.count(), 1)
        self.assertEqual(user_profile.skills.first(), self.skill)

    def test_should_raise_validation_error_when_creating_user_profile_with_empty_description(
        self,
    ):
        """
        Test that checks if creating a UserProfile with empty description raises a ValidationError.
        """
        with self.assertRaises(ValidationError):
            user_profile = UserProfile(user=self.user, description="")
            user_profile.full_clean()


class TestRatingModel(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="12345")
        self.user2 = User.objects.create_user(username="testuser2", password="12345")

    def tearDown(self):
        Rating.objects.all().delete()

    def test_should_increase_rating_count_and_set_correct_fields_after_rating_creation(
        self,
    ):
        """
        Test that checks if creating a Rating increases the count and sets the fields correctly.
        """
        rating = Rating.objects.create(
            user=self.user1, code_quality=4.5, solution_time=3.5, contact=5.0
        )
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(rating.code_quality, 4.5)
        self.assertEqual(rating.solution_time, 3.5)
        self.assertEqual(rating.contact, 5.0)

    def test_should_raise_validation_error_when_creating_rating_with_fields_out_of_valid_range(
        self,
    ):
        """
        Test that checks if creating a Rating with a field value outside of the valid range raises a ValidationError.
        """
        with self.assertRaises(ValidationError):
            rating = Rating.objects.create(
                user=self.user1, code_quality=-0.1, solution_time=3.5, contact=5.0
            )
            rating.full_clean()

        with self.assertRaises(ValidationError):
            rating = Rating.objects.create(
                user=self.user2, code_quality=10.1, solution_time=3.5, contact=5.0
            )
            rating.full_clean()

    def test_should_accept_minimum_valid_field_values(self):
        """
        Test that checks if creating a Rating with the minimum valid field values is successful.
        """
        rating = Rating.objects.create(
            user=self.user1, code_quality=0, solution_time=0, contact=0
        )
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(rating.code_quality, 0)
        self.assertEqual(rating.solution_time, 0)
        self.assertEqual(rating.contact, 0)

    def test_should_accept_maximum_valid_field_values(self):
        """
        Test that checks if creating a Rating with the maximum valid field values is successful.
        """
        rating = Rating.objects.create(
            user=self.user2, code_quality=10, solution_time=10, contact=10
        )
        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(rating.code_quality, 10)
        self.assertEqual(rating.solution_time, 10)
        self.assertEqual(rating.contact, 10)


class TestGetProfilePicturePath(TestCase):
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
