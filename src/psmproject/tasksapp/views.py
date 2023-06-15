from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView


from tasksapp.models import Task, TaskAttachment


class UserTasksListView(LoginRequiredMixin, ListView):
    """
    This View displays list of tasks created by user (client), ordered from newest. Tasks can be
    filtered by URL parameter "q" which will be searched in task title or task description
    """
    model = Task
    paginate_by = 10
    search_phrase_min = 3

    def get_queryset(self):
        phrase = self.request.GET.get("q", "")
        queryset = Task.objects.filter(client=self.request.user).order_by("-id")
        if len(phrase) >= UserTasksListView.search_phrase_min:
            queryset = queryset.filter(Q(title__contains=phrase) | Q(description__contains=phrase))
        return queryset
