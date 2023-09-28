from chatapp.models import Chat
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
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
        if self.object.selected_offer:
            try:
                context["chat_id"] = Chat.objects.get(object_id=self.object.id).id
            except ObjectDoesNotExist:
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    "No chat related to this task was found, please contact the administrator.",
                )
            except MultipleObjectsReturned:
                messages.add_message(
                    self.request,
                    messages.WARNING,
                    "More than one chat was found for this task, please contact the administrator.",
                )
        return context


class TaskPreviewView(TaskDetailView):
    """
    This View displays task details and all attachments, without possibility to edit anything
    """

    template_name = "tasksapp/task_preview.html"


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
        if task.status >= Task.TaskStatus.ON_GOING:
            return False
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=TaskDeleteView.allowed_groups).exists()
        return user == task.client or in_allowed_group

    def handle_no_permission(self):
        redirect_url = self.get_success_url()
        return HttpResponseRedirect(redirect_url)
