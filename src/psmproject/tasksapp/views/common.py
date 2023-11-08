from chatapp.models import Chat
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render  # noqa
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView

from ..models import Task


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
    allowed_groups = [
        settings.GROUP_NAMES.get("MODERATOR"),
    ]

    template_name = "tasksapp/task_confirm_delete.html"

    def get_success_url(self):
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=TaskDeleteView.allowed_groups).exists()
        if in_allowed_group:
            return reverse_lazy("tasks-all-list")
        return reverse_lazy("tasks-client-list")

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


class SearchListView(ListView):
    """
    List View with search form
    """

    model = Task
    template_name_suffix = "s_list"
    paginate_by = 10
    search_form_class = None
    search_phrase_min = 3

    def search(self, queryset, form):
        """
        method filtering standard queryset using form data. Must be implemente in inheriting views. Called in
        get_queryset()
        """
        raise NotImplementedError

    def get_queryset(self, **kwargs):
        """
        returns queryset of all Tasks. Tasks can be filtered by the query sent with POST method. Tasks can be filtered
        by username (form field "user"), title or description (form field "query")
        """
        queryset = self.model.objects.all().order_by("-id")
        form = kwargs.get("form")
        if not form or not form.is_valid():
            return queryset
        queryset = self.search(queryset, form)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get("form")
        if form:
            context["form"] = form
            context["filtered"] = True
        else:
            context["form"] = self.search_form_class()
        return context

    def get(self, request, *args, **kwargs):
        form = self.search_form_class(request.GET) if bool(request.GET) else None
        self.object_list = self.get_queryset(form=form)
        return self.render_to_response(self.get_context_data(form=form))
