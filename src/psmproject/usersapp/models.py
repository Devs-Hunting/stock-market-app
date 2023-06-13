from django.contrib.auth.models import AbstractUser, Group
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
    - email_verified (BooleanField): Indicates whether the user's email has been verified.
    - group (ManyToManyField): The groups that the user belongs to.
    - USERNAME_FIELD (str): The field to use as the unique identifier for authentication (set to 'email').
    """

    email_verified = models.BooleanField(default=False)
    group = models.ManyToManyField(Group)

    USERNAME_FIELD = "email"

    class Meta:
        swappable = "AUTH_USER_MODEL"


class Notification(models.Model):
    """Represents a notification.

    Fields:
    - id (AutoField): The unique identifier for the notification.
    - user_id (ForeignKey): The user associated with the notification.
    - content (CharField): The content of the notification (maximum length: 50 characters).
    - created_at (DateTimeField): The date and time when the notification was created (automatically set on creation).
    """

    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, db_column="id", on_delete=models.CASCADE)
    content = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    """User profile with basic information.

    Fields:
    - id (AutoField): Unique identifier.
    - user_id (ForeignKey): Associated user.
    - first_name (CharField, max_length=50): User's first name.
    - last_name (CharField, max_length=50): User's last name.
    - profile_picture (ImageField, optional): User's profile picture.
    - description (TextField, max_length=200): User's description.
    - skills (ManyToManyField): Associated skills.
    - created_at (DateTimeField): Creation timestamp.
    - updated_at (DateTimeField): Last update timestamp.
    """

    @staticmethod
    def get_profile_picture_path(instance, filename):
        """Generate the file path and filename for the profile picture upload.

        Arguments:
        - instance: The UserProfile instance.
        - filename: The original filename of the uploaded file.

        Returns:
        The file path and filename in the format: 'profile_pictures/<user_id>/<filename>'
        """
        return f"profile_pictures/{instance.user_id}/{filename}"

    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, db_column="id", on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    profile_picture = models.ImageField(upload_to=get_profile_picture_path, null=True, blank=True)
    description = models.TextField(max_length=200)
    skills = models.ManyToManyField(Skill)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
