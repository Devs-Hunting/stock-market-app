from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView, View

from .forms import BlockUserForm
from .helpers import SpecialUserMixin
from .models import BlockedUser


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


class BlockUserView(SpecialUserMixin, CreateView):
    """
    Class based View for adding user as a blocked user.
    Blocked user will be added to the group of blocked users.
    It requires the user to be logged in and to be a special user.
    """

    model = BlockedUser
    form_class = BlockUserForm
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        """Assign blocked user to the group of blocked users and blocking user as logged user"""
        form.instance.blocking_user = self.request.user
        blocked_user = form.cleaned_data["blocked_user"]
        blocked_user.groups.add(Group.objects.get(name=settings.GROUP_NAMES.get("BLOCKED_USER")))
        return super().form_valid(form)


class BlockUserDetailView(SpecialUserMixin, DetailView):
    """
    Class based view for showing blocked user details.
    """

    model = BlockedUser
    template_name = "usersapp/block_user_detail.html"


class BlockUserListView(SpecialUserMixin, ListView):
    """
    Class based view for showing list of blocked users.
    """

    model = BlockedUser
    template_name = "usersapp/blocked_users_list.html"
