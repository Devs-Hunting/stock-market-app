from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render  # noqa
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView

from ..models import Task

# the group names should be defined somewhere in settings in the future
ADMINISTRATOR = "ADMINISTRATOR"
MODERATOR = "MODERATOR"
ARBITER = "ARBITER"
CLIENT = "CLIENT"


class TaskDetailView(LoginRequiredMixin, DetailView):
    """
    This View displays task details and all attachments, without possibility to edit anything
    """

    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = self.object.attachments.all()
        return context


class TaskDeleteView(UserPassesTestMixin, DeleteView):
    """
    This view is used delete Task. Only task creator or moderator can do this.
    """

    model = Task
    allowed_groups = [MODERATOR]
    template_name = "tasksapp/task_confirm_delete.html"

    def get_success_url(self):
        role = self.request.session.get("role")
        if role in [None, CLIENT]:
            return reverse_lazy("tasks-client-list")
        return reverse_lazy("tasks-all-list")

    def test_func(self):
        task = self.get_object()
        if task.status > Task.TaskStatus.CLOSED:
            return False
        user = self.request.user
        in_allowed_group = user.groups.filter(
            name__in=TaskDeleteView.allowed_groups
        ).exists()
        return user == task.client or in_allowed_group

    def handle_no_permission(self):
        redirect_url = self.get_success_url()
        return HttpResponseRedirect(redirect_url)
