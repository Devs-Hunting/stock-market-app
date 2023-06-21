from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .forms import UserRegisterForm


class SignUpView(SuccessMessageMixin, CreateView):
    """
    View for user registration.
    Inherits from Django's CreateView and adds success message functionality.
    Attributes:
    - template_name (str): The name of the template to render for the registration page.
    - success_url (str): The URL to redirect to after successful registration.
    - form_class (UserRegisterForm): The form class to use for user registration.
    - success_message (str): The success message to display after successful registration.
    """

    template_name = "usersapp/register.html"
    success_url = reverse_lazy("login")
    form_class = UserRegisterForm
    success_message = "Account created"


class ProfileView(TemplateView, LoginRequiredMixin):
    """
    View for user profile.
    Inherits from Django's TemplateView and requires the user to be logged in.
    Attributes:
    - template_name (str): The name of the template to render for the profile page.
    """

    template_name = "usersapp/profile.html"
