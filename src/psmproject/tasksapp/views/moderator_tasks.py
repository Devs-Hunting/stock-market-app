from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render  # noqa
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import ListView

from ..forms.tasks import ModeratorUpdateTaskForm, TaskSearchModeratorForm
from ..models import Task


class TasksListView(UserPassesTestMixin, ListView):
    """
    This View displays all tasks, ordered from newest. Tasks can be filtered by username, and query phrase which is
    compared against task title and task description.
    Result list is limited/paginated
    View enabled only for administrators and moderators
    """

    model = Task
    template_name = "tasksapp/tasks_list_all.html"
    allowed_groups = [
        settings.GROUP_NAMES.get("ADMINISTRATOR"),
        settings.GROUP_NAMES.get("MODERATOR"),
    ]
    redirect_url = reverse_lazy("dashboard")
    paginate_by = 10
    search_form_class = TaskSearchModeratorForm
    search_phrase_min = 3

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=TasksListView.allowed_groups).exists()

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(TasksListView.redirect_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = kwargs.get("form") if "form" in kwargs else TasksListView.search_form_class()
        return context

    def get_queryset(self, **kwargs):
        """
        returns queryset of all Tasks, optionally filtered by user_id given by URL parameter "u" or title,
        description search_phrase, parameter "q"
        """
        queryset = Task.objects.all().order_by("-id")
        form = kwargs.get("form")
        if not form:
            return queryset
        username = form.cleaned_data.get("user", "")
        user = settings.AUTH_USER_MODEL.objects.filter(username=username).first()
        if username and user:
            queryset = queryset.filter(client=user)
        phrase = form.cleaned_data.get("query", "")
        if phrase and len(phrase) >= TasksListView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        return queryset

    def post(self, request, *args, **kwargs):
        form = TasksListView.search_form_class(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data())
        self.object_list = self.get_queryset(form=form)
        return self.render_to_response(self.get_context_data(form=form))


class TaskEditView(UserPassesTestMixin, UpdateView):
    """
    This View allows to edit existing task. Only client, administrator or moderator are allowed to edit.
    Task should be part of the URL
    """

    model = Task
    form_class = ModeratorUpdateTaskForm
    allowed_groups = [
        settings.GROUP_NAMES.get("ADMINISTRATOR"),
        settings.GROUP_NAMES.get("MODERATOR"),
    ]

    def get_success_url(self):
        task = self.get_object()
        return reverse("task-detail", kwargs={"pk": task.id})

    def test_func(self):
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=TaskEditView.allowed_groups).exists()
        return in_allowed_group

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(TasksListView.redirect_url)


class TaskDeleteView(UserPassesTestMixin, DeleteView):
    """
    This view is used delete Task. Only task creator, administrator or moderator can do this.
    """

    model = Task
    allowed_groups = [
        settings.GROUP_NAMES.get("ADMINISTRATOR"),
        settings.GROUP_NAMES.get("MODERATOR"),
    ]
    template_name = "tasksapp/task_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("tasks-moderator-list")

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
