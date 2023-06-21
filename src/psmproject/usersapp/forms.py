from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User



class UserRegisterForm(UserCreationForm):
    """
    A form for registering a new user.
    Inherits from Django's UserCreationForm and adds an additional field for email.
    Fields:
    - email (EmailField): The email address of the user.
    Meta:
    - model (User): The User model to use for registration.
    - fields (list): The fields to include in the form, in the specified order.
    Note: The inherited fields from UserCreationForm are:
        - username (CharField): The desired username for the user.
        - password1 (CharField): The first password field.
        - password2 (CharField): The second password field for password confirmation.
        - first_name (CharField): The first name of the user.
        - last_name (CharField): The last name of the user.
    """

    email = forms.EmailField()

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]
