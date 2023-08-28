from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render  # noqa
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from ..forms import ModeratorUpdateTaskForm
from ..models import Task


class TasksListView(UserPassesTestMixin, ListView):
    """
    This View displays all tasks, ordered from newest. Tasks can be filtered by URL parameter "q". Search phrase will
    be compared against task title or task description.
    Tasks can be filtered by the client(user) that created the task. URL parameter "u" with user id.
    Result list is limited/paginated
    View enabled only for staff users  (administrators, moderators, arbiters)
    """

    model = Task
    template_name = "tasksapp/tasks_list_all.html"
    allowed_groups = [
        settings.GROUP_NAMES.get("ADMINISTRATOR"),
        settings.GROUP_NAMES.get("MODERATOR"),
        settings.GROUP_NAMES.get("ARBITER"),
    ]
    redirect_url = reverse_lazy("dashboard")
    paginate_by = 10
    search_phrase_min = 3

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=TasksListView.allowed_groups).exists()

    def handle_no_permission(self):
        return HttpResponseRedirect(TasksListView.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role"] = self.request.session.get("role", "")
        return context

    def get_queryset(self):
        """
        returns queryset of all Tasks, optionally filtered by user_id given by URL parameter "u" or title,
        description search_phrase, parameter "q"
        """
        queryset = Task.objects.all().order_by("-id")
        user_id = self.request.GET.get("u", "")
        if user_id:
            try:
                user = settings.AUTH_USER_MODEL.objects.get(user_id)
                queryset = queryset.filter(client=user)
            except ObjectDoesNotExist:
                pass
        phrase = self.request.GET.get("q", "")
        if len(phrase) >= TasksListView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        return queryset


class TaskEditView(UserPassesTestMixin, UpdateView):
    """
    This View allows to edit existing task. Only client or moderator are allowed to edit.
    Task should be part of the URL
    """

    model = Task
    form_class = ModeratorUpdateTaskForm
    allowed_groups = [settings.GROUP_NAMES.get("MODERATOR")]

    def get_success_url(self):
        task = self.get_object()
        return reverse("task-detail", kwargs={"pk": task.id})

    def test_func(self):
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=TaskEditView.allowed_groups).exists()
        return in_allowed_group

    def handle_no_permission(self):
        return HttpResponseRedirect(self.get_success_url())


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
        in_allowed_group = user.groups.filter(name__in=TaskDeleteView.allowed_groups).exists()
        return user == task.client or in_allowed_group

    def handle_no_permission(self):
        redirect_url = self.get_success_url()
        return HttpResponseRedirect(redirect_url)
