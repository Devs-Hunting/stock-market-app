from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Skill(models.Model):
    """
    Represents a skill that can be associated with users.
    Fields:
    - id (AutoField): Unique identifier.
    - skill (CharField): The name of the skill (maximum length: 40 characters).
    """

    skill = models.CharField(max_length=40, unique=True, verbose_name=_("skill"))

    def clean(self):
        """
        Cleans the data by calling the clean method of the superclass and then performs additional validation checks.
        """
        super().clean()
        self.validate_max_length()
        self.validate_unique_name()

    def validate_max_length(self):
        if len(self.skill) > 40:
            raise ValidationError(_(f"Ensure this value has at most 40 characters (it has {len(self.skill)}."))

    def validate_unique_name(self):
        try:
            Skill.objects.get(skill=self.skill)
            raise ValidationError(_(f"Skill with this {self.skill} name already exists."))
        except Skill.DoesNotExist:
            pass

    def __str__(self):
        return self.skill

    def __repr__(self):
        return _(f"Skill(id={self.id}, skill={self.skill})")


class Notification(models.Model):
    """
    Represents a notification.
    Fields:
    - id (AutoField): Unique identifier.
    - user (ForeignKey): The user associated with the notification.
    - content (CharField): The content of the notification (maximum length: 150 characters).
    - created_at (DateTimeField): The date and time when the notification was created (automatically set on creation).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications", verbose_name=_("user")
    )
    content = models.CharField(max_length=150, blank=False, verbose_name=_("content"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))

    def __str__(self):
        return self.content

    def __repr__(self):
        return _(
            f"Notification(id={self.id}, user={self.user}, content='{self.content}', created_at={self.created_at})"
        )


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


class UserProfile(models.Model):
    """
    User profile with basic information.
    Fields:
    - id (AutoField): Unique identifier.
    - user (OneToOneField): Associated user.
    - profile_picture (ImageField, optional): User's profile picture.
    - description (TextField): User's description.
    - skills (ManyToManyField): Associated skills.
    - created_at (DateTimeField): Creation timestamp.
    - updated_at (DateTimeField): Last update timestamp.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile", verbose_name=_("user")
    )
    profile_picture = models.ImageField(
        upload_to=get_profile_picture_path, null=True, blank=True, verbose_name=_("profile picture")
    )
    description = models.TextField(verbose_name=_("description"))
    skills = models.ManyToManyField(Skill, verbose_name=_("skills"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("updated at"))

    def __str__(self):
        return _(f"Profile for user: {self.user}")

    def __repr__(self):
        return _(f"UserProfile(user={self.user}, description={self.description})")


class Rating(models.Model):
    """
    User rating for different aspects.
    Fields:
    - user (OneToOneField): Associated user.
    - code_quality (DecimalField): User's rating for code quality.
    - solution_time (DecimalField): User's rating for solution time.
    - contact (DecimalField): User's rating for contact ease.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="rating", verbose_name=_("user")
    )
    code_quality = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_("code quality"),
    )
    solution_time = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_("solution time"),
    )
    contact = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        verbose_name=_("contact"),
    )

    def __str__(self):
        return _(f"Rating for {self.user}")

    def __repr__(self):
        return _(
            f"Rating(id={self.id}, user={self.user}, code_quality={self.code_quality},\
            solution_time={self.solution_time}, contact={self.contact})"
        )


class BlockedUser(models.Model):
    """
    Represents a user who has been blocked.
    Fields:
    - id (AutoField): Unique identifier.
    - blocked_user (ForeignKey): The user who has been blocked.
    - blocking_user (ForeignKey): The user who initiated the block.
    - blocking_start_date (DateTimeField): The date and time when the blocking occurred.
    - blocking_end_date (DateTimeField): The date and time when the blocking ends.
    - reason (TextField): A brief description explaining why the user was blocked.
    """

    blocked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="blocked", verbose_name=_("blocked user")
    )
    blocking_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="blocking", verbose_name=_("blocking user")
    )
    blocking_start_date = models.DateTimeField(auto_now_add=True, verbose_name=_("blocking start date"))
    blocking_end_date = models.DateTimeField(verbose_name=_("blocking end date"))
    reason = models.TextField(verbose_name=_("reason"))

    def __str__(self):
        return _(f"Blocked user {self.blocked_user}")

    def __repr__(self):
        return _(
            f"BlockedUser(id={self.id}, blocked_user_id={self.blocked_user.id}, "
            f"blocking_user_id={self.blocking_user.id}, "
            f"blocking_start_date='{self.blocking_start_date}', "
            f"blocking_end_date='{self.blocking_end_date}', "
            f"reason='{self.reason}')"
        )
