import datetime

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import render  # noqa
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView
from usersapp.helpers import ModeratorMixin

from ..forms.tasks import ModeratorUpdateTaskForm, TaskSearchModeratorForm
from ..models import Task

User = get_user_model()


class TasksListView(ModeratorMixin, ListView):
    """
    This View displays all tasks, ordered from newest. Tasks can be filtered by username, and query phrase which is
    compared against task title and task description.
    Result list is limited/paginated
    View enabled only for administrators, arbiters and moderators
    """

    model = Task
    template_name = "tasksapp/tasks_list_moderator.html"
    paginate_by = 10
    search_form_class = TaskSearchModeratorForm
    search_phrase_min = 3

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "form" in kwargs:
            context["form"] = kwargs.get("form")
            context["filtered"] = True
        else:
            context["form"] = TasksListView.search_form_class()
        return context

    def get_queryset(self, **kwargs):
        """
        returns queryset of all Tasks. Tasks can be filtered by the query sent with POST method. Tasks can be filtered
        by username (form field "user"), title or description (form field "query")
        """
        queryset = Task.objects.all().order_by("-id")
        form = kwargs.get("form")
        if not form:
            return queryset
        username = form.cleaned_data.get("username", "")
        user = User.objects.filter(username=username).first()
        if username:
            queryset = queryset.filter(client=user)
        phrase = form.cleaned_data.get("query", "")
        if phrase and len(phrase) >= TasksListView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        return queryset

    def get(self, request, *args, **kwargs):
        form = TasksListView.search_form_class(request.GET)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data())
        self.object_list = self.get_queryset(form=form)
        return self.render_to_response(self.get_context_data(form=form))


class TasksNewListView(ModeratorMixin, ListView):
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
        search_start = datetime.datetime.now() - datetime.timedelta(days=TasksNewListView.days)
        queryset = Task.objects.filter(updated__gte=search_start).order_by("-id")
        return queryset


class TaskEditView(ModeratorMixin, UpdateView):
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


class TaskDetailView(ModeratorMixin, DetailView):
    """
    This View displays offer details without possibility to edit anything. Version for moderator
    """

    model = Task
    template_name_suffix = "_detail_moderator"
