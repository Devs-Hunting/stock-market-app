from chatapp.models import ComplaintChat, TaskChat
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render  # noqa
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from tasksapp.mixins import InstanceChatDetailsMixin
from usersapp.helpers import UsersNonBlockedTestMixin

from ..forms.complaint import ComplaintForm
from ..models import Complaint, Task


class TaskDetailView(LoginRequiredMixin, InstanceChatDetailsMixin, DetailView):
    """
    This View displays task details and all attachments, without possibility to edit anything
    """

    model = Task
    chat_model = TaskChat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = self.object.attachments.all()
        context["complaint"] = self.object.complaints.all().first()
        context["is_ongoing"] = self.object.status == Task.TaskStatus.ON_GOING
        context |= self.additional_context_data()
        return context

    def additional_context_data(self):
        additional_context = {}
        if self.object.selected_offer:
            additional_context |= self.chat_context_data() or {}
            if self.object.selected_offer.solution:
                additional_context["solution_attachments"] = self.object.selected_offer.solution.attachments.all()
        return additional_context


class TaskPreviewView(TaskDetailView):
    """
    This View displays task details and all attachments, without possibility to edit anything
    """

    template_name = "tasksapp/task_preview.html"


class TaskDeleteView(UsersNonBlockedTestMixin, DeleteView):
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


class ComplaintCreateView(UsersNonBlockedTestMixin, CreateView):
    """
    View to create a Complaint for Task by logged-in user client or contractor.
    """

    model = Complaint
    form_class = ComplaintForm

    def get_success_url(self) -> str:
        return reverse("complaint-detail", kwargs={"pk": self.object.id})

    def dispatch(self, request, *args, **kwargs):
        task_id = kwargs.get("task_pk")
        self.task = Task.objects.filter(id=task_id).first()
        if not self.task:
            messages.warning(self.request, "task not found")
            return HttpResponseRedirect(reverse("tasks-client-list"))
        return super().dispatch(request, *args, **kwargs)

    def test_func(self):
        user = self.request.user
        if self.task.status == Task.TaskStatus.ON_GOING and self.task.selected_offer:
            return user in [self.task.selected_offer.contractor, self.task.client]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = self.task
        return context

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(reverse("task-detail", kwargs={"pk": self.task.id}))

    def form_valid(self, form):
        """Assign current user as complainant and change status of task to OBJECTIONS"""
        form.instance.complainant = self.request.user
        form.instance.task = self.task
        self.task.status = Task.TaskStatus.OBJECTIONS
        self.task.save(update_fields=["status"])
        return super().form_valid(form)


class ComplaintEditView(UserPassesTestMixin, UpdateView):
    """
    View to edit a complaint by logged-in user author of the complaint.
    """

    model = Complaint
    form_class = ComplaintForm

    def get_success_url(self):
        complaint = self.get_object()
        return reverse("complaint-detail", kwargs={"pk": complaint.id})

    def test_func(self):
        complaint = self.get_object()
        user = self.request.user
        return user == complaint.complainant

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        complaint = self.get_object()
        context["task"] = complaint.task
        return context

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(self.get_success_url())


class ComplaintDetailView(LoginRequiredMixin, InstanceChatDetailsMixin, DetailView):
    """
    Detail view for a complaint with all attachments.
    """

    model = Complaint
    chat_model = ComplaintChat

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = self.object.attachments.all()
        context["is_complainant"] = self.request.user == self.object.complainant
        context["is_client"] = self.request.user == self.object.task.client
        if self.object.arbiter:
            context |= self.chat_context_data()
        return context


class ComplaintDeleteView(UsersNonBlockedTestMixin, DeleteView):
    """
    View to delete a complaint by logged-in user author of the complaint.
    To delete a complaint attribute closed must be false.
    """

    model = Complaint
    template_name = "tasksapp/complaint_confirm_delete.html"

    def get_success_url(self):
        complaint = self.get_object()
        task = complaint.task
        return reverse("task-detail", kwargs={"pk": task.id})

    def test_func(self):
        complaint = self.get_object()
        user = self.request.user
        if complaint.closed:
            messages.warning(self.request, "Complaint was closed. It can't be deleted")
            return False
        return user == complaint.complainant

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(self.get_success_url())

    def form_valid(self, form):
        """Change status of task to ON-GOING"""
        complaint = self.get_object()
        complaint.task.status = Task.TaskStatus.ON_GOING
        complaint.task.save()
        return super().form_valid(form)
