from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from usersapp.models import Skill

from ..forms import TaskForm, UpdateTaskForm
from ..models import Task

# the group names should be defined somewhere in settings in the future
ADMINISTRATOR = "ADMINISTRATOR"
MODERATOR = "MODERATOR"
ARBITER = "ARBITER"
CLIENT = "CLIENT"


class TasksListBaseView(LoginRequiredMixin, ListView):
    """
    This is a base view class for displaying list of tasks created by currently logged-in user (client), ordered from
    newest. Tasks can be filtered by URL parameter "q". Search phrase will be compared against task title or task
    description. Result list is limited/paginated
    """

    model = Task
    template_name_suffix = "s_list"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        phrase = self.request.GET.get("q", "")
        queryset = Task.objects.filter(client=self.request.user).order_by("-id")
        if len(phrase) >= TasksListBaseView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        return queryset


class TasksCurrentListView(TasksListBaseView):
    """
    Extension of TasksListBaseView, displays only active tasks created by current user.
    """

    template_name_suffix = "s_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status__lt=Task.TaskStatus.COMPLETED)


class TasksHistoricalListView(TasksListBaseView):
    """
    Extension of TasksListBaseView, displays only historical tasks created by current user.
    """

    template_name_suffix = "s_history_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status__gte=Task.TaskStatus.COMPLETED)


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
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skills = Skill.objects.all()
        context["skills"] = [model_to_dict(skill) for skill in list(skills)]
        return context


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skills = Skill.objects.all()
        if self.object:
            task_skills = self.object.skills.all()
            context["task_skills"] = list(task_skills)
            skills = skills.difference(task_skills)
        context["skills"] = [model_to_dict(skill) for skill in list(skills)]
        return context
