from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render  # noqa
from django.views.generic.list import ListView

from ..models import Task

# the group names should be defined somewhere in settings in the future
ADMINISTRATOR = "ADMINISTRATOR"
MODERATOR = "MODERATOR"
ARBITER = "ARBITER"
CLIENT = "CLIENT"


class TasksListView(LoginRequiredMixin, ListView):
    """
    This View displays list of tasks which contractor is currently assigned-to, ordered from newest. Tasks can be
    filtered by URL parameter "q". Search phrase will be compared against task title or task description.
    Result list is limited/paginated
    """

    model = Task
    template_name_suffix = "s_contractor_list"
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        phrase = self.request.GET.get("q", "")
        # queryset = Task.objects.filter(selected_order.contractor=self.request.user).order_by("-id")
        queryset = Task.objects.all().order_by("-id")
        if len(phrase) >= TasksListView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        return queryset
