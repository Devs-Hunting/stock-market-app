import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render  # noqa
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from usersapp.helpers import SpecialUserMixin

from ..forms.tasks import ModeratorUpdateTaskForm, TaskSearchModeratorForm
from ..models import Task
from .common import SearchListView

User = get_user_model()


class TasksListView(SpecialUserMixin, SearchListView):
    """
    This View displays all tasks, ordered from newest. Tasks can be filtered by username, and query phrase which is
    compared against task title and task description.
    Result list is limited/paginated
    View enabled only for administrators, arbiters and moderators
    """

    model = Task
    template_name_suffix = "s_list_moderator"
    paginate_by = 10
    search_form_class = TaskSearchModeratorForm
    search_phrase_min = 3

    def search(self, queryset, form):
        """
        search method
        """
        username = form.cleaned_data.get("username", "")
        user = User.objects.filter(username=username).first()
        if username:
            queryset = queryset.filter(client=user)
        phrase = form.cleaned_data.get("query", "")
        if phrase and len(phrase) >= TasksListView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        return queryset


class TasksNewListView(SpecialUserMixin, ListView):
    """
    This View displays newest tasks. Result list is limited/paginated
    View enabled only for administrators, arbiters and moderators
    """

    model = Task
    template_name_suffix = "s_list_moderator"
    days = 3
    paginate_by = 10

    def get_queryset(self, **kwargs):
        """
        returns queryset of tasks not older than X days before. X is a class view parameter
        """
        search_start = now() - datetime.timedelta(days=TasksNewListView.days)
        queryset = Task.objects.filter(updated__gte=search_start).order_by("-id")
        return queryset


class TaskEditView(SpecialUserMixin, UpdateView):
    """
    This View allows to edit existing task. Only client, administrator or moderator are allowed to edit.
    Task should be part of the URL
    """

    model = Task
    form_class = ModeratorUpdateTaskForm
    template_name = "tasksapp/task_form_moderator.html"

    def get_success_url(self):
        task = self.get_object()
        return reverse("task-moderator-detail", kwargs={"pk": task.id})


class TaskDetailView(SpecialUserMixin, DetailView):
    """
    This View displays offer details without possibility to edit anything. Version for moderator
    """

    model = Task
    template_name_suffix = "_detail_moderator"
