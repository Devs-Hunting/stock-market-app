from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Group
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
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
    Full block user will be added to the blocked users group and is marked as inactive.
    """

    model = BlockedUser
    form_class = BlockUserForm
    success_url = reverse_lazy("dashboard")

    def full_block_user(self, user):
        user.groups.add(Group.objects.get(name=settings.GROUP_NAMES.get("BLOCKED_USER")))
        user.is_active = False
        user.save()
        return user

    def form_valid(self, form):
        form.instance.blocking_user = self.request.user
        blocked_user = form.cleaned_data["blocked_user"]
        full_blocking = form.cleaned_data["full_blocking"]
        if full_blocking:
            self.full_block_user(blocked_user)
        else:
            blocked_user.groups.add(Group.objects.get(name=settings.GROUP_NAMES.get("BLOCKED_USER")))
        return super().form_valid(form)


class BlockedUserDetailView(SpecialUserMixin, DetailView):
    """
    Class based view for showing blocked user details.
    """

    model = BlockedUser
    template_name = "usersapp/block_user_detail.html"

    def check_active_blocking(self, blocking_end_date):
        if blocking_end_date is None:
            return False
        return blocking_end_date > now()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update({"active_blocking": self.check_active_blocking(self.object.blocking_end_date)})
        return context


class BlockedUsersListView(SpecialUserMixin, ListView):
    """
    Class based view for showing list of blocked users with a active blocking.
    """

    model = BlockedUser
    template_name = "usersapp/blocked_users_list.html"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        queryset = BlockedUser.objects.filter(
            Q(blocking_end_date__gt=now()) | Q(blocking_end_date__isnull=True)
        ).order_by("-id")

        phrase = self.request.GET.get("q", "")
        if len(phrase) >= BlockedUsersListView.search_phrase_min:
            queryset = queryset.filter(Q(blocked_user__username__contains=phrase) | Q(reason__contains=phrase))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        active_ban_users = BlockedUser.objects.filter(blocking_end_date__gte=now(), full_blocking=False)

        context.update({"active_ban_users": active_ban_users})
        return context
