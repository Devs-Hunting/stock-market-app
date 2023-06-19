from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from .forms import UserRegisterForm


class SignUpView(SuccessMessageMixin, CreateView):
    template_name = "usersapp/register.html"
    success_url = reverse_lazy("login")
    form_class = UserRegisterForm
    success_message = "Account created"


class ProfileView(TemplateView, LoginRequiredMixin):
    template_name = "usersapp/profile.html"
