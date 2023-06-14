from django.contrib.auth.models import AbstractUser
from django.db import models


class Skill(models.Model):
    """Represents a skill that can be associated with users.
    Fields:
    - id (AutoField): The unique identifier for the skill.
    - skill (CharField): The name of the skill (maximum length: 20 characters).
    """

    id = models.AutoField(primary_key=True)
    skill = models.CharField(max_length=20)


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser.
    Fields:
    - USERNAME_FIELD (str): The field to use as the unique identifier for authentication (set to 'email').
    """

    USERNAME_FIELD = "email"

    class Meta:
        swappable = "AUTH_USER_MODEL"


class Notification(models.Model):
    """Represents a notification.
    Fields:
    - id (AutoField): The unique identifier for the notification.
    - user (ForeignKey): The user associated with the notification.
    - content (CharField): The content of the notification (maximum length: 50 characters).
    - created_at (DateTimeField): The date and time when the notification was created (automatically set on creation).
    """

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    content = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    """
    User profile with basic information.
    Fields:
    - id (AutoField): Unique identifier.
    - user (ForeignKey): Associated user.
    - profile_picture (ImageField, optional): User's profile picture.
    - description (TextField): User's description.
    - skills (ManyToManyField): Associated skills.
    - created_at (DateTimeField): Creation timestamp.
    - updated_at (DateTimeField): Last update timestamp.
    """

    @staticmethod
    def get_profile_picture_path(instance, filename):
        """
        Generate the file path and filename for the profile picture upload.
        Arguments:
        - instance: The UserProfile instance.
        - filename: The original filename of the uploaded file.

        Returns:
        The file path and filename in the format: 'profile_pictures/<user_id>/<filename>'
        """
        return f"profile_pictures/{instance.user.id}/{filename}"

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(
        upload_to=get_profile_picture_path, null=True, blank=True
    )
    description = models.TextField()
    skills = models.ManyToManyField(Skill)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Rating(models.Model):
    """
    User rating for different aspects.
    Fields:
    - id (AutoField): Unique identifier.
    - user (ForeignKey): Associated user.
    - code_quality (DecimalField): User's rating for code quality.
    - solution_time (DecimalField): User's rating for solution time.
    - contact (DecimalField): User's rating for contact ease.
    """

    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="rating")
    code_quality = models.DecimalField(max_digits=2, decimal_places=1)
    solution_time = models.DecimalField(max_digits=2, decimal_places=1)
    contact = models.DecimalField(max_digits=2, decimal_places=1)
