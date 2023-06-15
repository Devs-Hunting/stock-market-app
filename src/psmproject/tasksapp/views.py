from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render  # noqa
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from tasksapp.models import Task

# the group names should be defined somewhere in settings in the future
ADMINISTRATOR = "ADMINISTRATOR"
MODERATOR = "MODERATOR"
ARBITER = "ARBITER"


class ClientTasksListView(LoginRequiredMixin, ListView):
    """
    This View displays list of tasks created by currently logged-in user (client), ordered from newest. Tasks can be
    filtered by URL parameter "q". Search phrase will be compared against task title or task description.
    Result list is limited/paginated
    """

    model = Task
    template_name_suffix = "_list"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        phrase = self.request.GET.get("q", "")
        queryset = Task.objects.filter(client=self.request.user).order_by("-id")
        if len(phrase) >= ClientTasksListView.search_phrase_min:
            queryset = queryset.filter(
                Q(title__contains=phrase) | Q(description__contains=phrase)
            )
        return queryset


class StaffTasksListView(UserPassesTestMixin, ListView):
    """
    This View displays all tasks, ordered from newest. Tasks can be filtered by URL parameter "q". Search phrase will
    be compared against task title or task description.
    Tasks can be filtered by the client(user) that created the task. URL parameter "u" with user id.
    Result list is limited/paginated
    View enabled only for staff users  (administrators, moderators, arbiters)
    """

    model = Task
    template_name_suffix = "_list"
    allowed_groups = [ADMINISTRATOR, MODERATOR, ARBITER]
    redirect_url = reverse_lazy("dashboard")
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        phrase = self.request.GET.get("q", "")
        queryset = Task.objects.all().order_by("-id")
        if len(phrase) >= ClientTasksListView.search_phrase_min:
            queryset = queryset.filter(
                Q(title__contains=phrase) | Q(description__contains=phrase)
            )
        return queryset

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=StaffTasksListView.allowed_groups).exists()

    def handle_no_permission(self):
        return HttpResponseRedirect(TaskDetailView.redirect_url)


class TaskDetailView(LoginRequiredMixin, DetailView):
    """
    This View displays task details and all attachments, without possibility to edit anything
    """

    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = self.object.attachments.all()
        return context


class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    This View creates new tasks with logged-in user as a client
    """

    model = Task

    def form_valid(self, form):
        """Assign current user to the new task"""
        form.instance.client = self.request.user
        self.object = form.save()
        return super().form_valid(form)


class TaskEditView(UserPassesTestMixin, UpdateView):
    """
    This View allows to edit existing task. Only client or moderator are allowed to edit.
    Task should be part of the URL
    """

    model = Task
    allowed_groups = [MODERATOR]
    redirect_url = reverse_lazy("tasks-list")

    def test_func(self):
        task = self.get_object()
        user = self.request.user
        in_allowed_group = user.groups.filter(
            name__in=StaffTasksListView.allowed_groups
        ).exists()
        return task.client == self.request.user or in_allowed_group

    def handle_no_permission(self):
        return HttpResponseRedirect(TaskEditView.redirect_url)


class TaskDeleteView(UserPassesTestMixin, DeleteView):
    """
    This view is used delete Task. Only task creator or moderator can do this.
    """

    model = Task
    allowed_groups = [MODERATOR]
    template_name = "tasksapp/task_confirm_delete.html"

    def get_success_url(self):
        return reverse_lazy("tasks-client-list")

    def test_func(self):
        user = self.request.user
        in_allowed_group = user.groups.filter(
            name__in=TaskDeleteView.allowed_groups
        ).exists()
        return user == self.get_object().task.client or in_allowed_group

    def handle_no_permission(self):
        redirect_url = self.get_success_url()
        return HttpResponseRedirect(redirect_url)
