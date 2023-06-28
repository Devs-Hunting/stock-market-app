from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from ..forms import TaskForm, UpdateTaskForm
from ..models import Task

# the group names should be defined somewhere in settings in the future
ADMINISTRATOR = "ADMINISTRATOR"
MODERATOR = "MODERATOR"
ARBITER = "ARBITER"
CLIENT = "CLIENT"


class TasksListView(LoginRequiredMixin, ListView):
    """
    This View displays list of active tasks created by currently logged-in user (client), ordered from newest. Tasks can be
    filtered by URL parameter "q". Search phrase will be compared against task title or task description.
    Result list is limited/paginated
    """

    model = Task
    template_name_suffix = "s_list"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        phrase = self.request.GET.get("q", "")
        queryset = Task.objects.filter(
            client=self.request.user, status__lt=Task.TaskStatus.COMPLETED
        ).order_by("-id")
        if len(phrase) >= TasksListView.search_phrase_min:
            queryset = queryset.filter(
                Q(title__contains=phrase) | Q(description__contains=phrase)
            )
        return queryset


class TasksHistoricalListView(LoginRequiredMixin, ListView):
    """
    This View displays list of historical (completed / cancelled) tasks created by currently logged-in user (client),
    ordered from newest. Tasks can be filtered by URL parameter "q". Search phrase will be compared against task title
    or task description.
    Result list is limited/paginated
    """

    model = Task
    template_name_suffix = "s_historical_list"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        phrase = self.request.GET.get("q", "")
        queryset = Task.objects.filter(
            client=self.request.user, status__ge=Task.TaskStatus.COMPLETED
        ).order_by("-id")
        if len(phrase) >= TasksListView.search_phrase_min:
            queryset = queryset.filter(
                Q(title__contains=phrase) | Q(description__contains=phrase)
            )
        return queryset


class TaskCreateView(LoginRequiredMixin, CreateView):
    """
    This View creates new tasks with logged-in user as a client
    """

    model = Task
    form_class = TaskForm
    success_url = reverse_lazy("tasks-client-list")

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
    form_class = UpdateTaskForm

    def get_success_url(self):
        task = self.get_object()
        return reverse("task-detail", kwargs={"pk": task.id})

    def test_func(self):
        task = self.get_object()
        return task.client == self.request.user

    def handle_no_permission(self):
        return HttpResponseRedirect(self.get_success_url())
