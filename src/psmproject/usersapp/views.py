from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView, View


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View for user profile.
    Inherits from Django's TemplateView and requires the user to be logged in.
    Attributes:
    - template_name (str): The name of the template to render for the profile page.
    """

    template_name = "usersapp/profile.html"


class SetRoleView(View):
    def post(self, request, *args, **kwargs):
        role_id = kwargs["role_id"]
        group = request.user.groups.filter(id=role_id).first()
        if group:
            request.session["role"] = role_id
            request.session["role_name"] = group.name

        redirect_url = reverse("dashboard")
        return HttpResponseRedirect(redirect_url)
