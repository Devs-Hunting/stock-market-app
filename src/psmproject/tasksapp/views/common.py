from chatapp.models import Chat
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.shortcuts import render  # noqa
from django.urls import reverse, reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ..forms.complaint import ComplaintForm
from ..models import Complaint, Task


class TaskDetailView(LoginRequiredMixin, DetailView):
    """
    This View displays task details and all attachments, without possibility to edit anything
    """

    model = Task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = self.object.attachments.all()
        context["complaint"] = self.object.complaints.all().first()
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


class ComplaintCreateView(LoginRequiredMixin, CreateView):
    """
    View to create a Complaint for Task by logged-in user client or contractor.
    """

    model = Complaint
    form_class = ComplaintForm

    def get_success_url(self) -> str:
        complaint = Complaint.objects.get(id=self.object.id)
        return reverse("complaint-detail", kwargs={"pk": complaint.id})

    def dispatch(self, request, *args, **kwargs):
        task_id = kwargs.get("task_pk")
        self.task = Task.objects.filter(id=task_id).first()
        url = reverse("task-detail", kwargs={"pk": task_id})
        if not self.task:
            messages.warning(self.request, "task not found")
            return HttpResponseRedirect(url)
        if self.task.status == Task.TaskStatus.CANCELLED:
            messages.warning(self.request, "task was cancelled")
            return HttpResponseRedirect(url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = self.task
        return context

    def form_valid(self, form):
        """Assign current user as complainant and change status of task to OBJECTIONS"""
        form.instance.complainant = self.request.user
        form.instance.task = self.task
        self.task.status = Task.TaskStatus.OBJECTIONS
        self.task.save()
        return super().form_valid(form)


class ComplaintEditView(LoginRequiredMixin, UpdateView):
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


class ComplaintDetailView(LoginRequiredMixin, DetailView):
    """
    Detail view for a complaint with all attachments.
    """

    model = Complaint

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["attachments"] = self.object.attachments.all()
        context["is_complainant"] = self.request.user == self.object.complainant
        return context


class ComplaintDeleteView(LoginRequiredMixin, DeleteView):
    """
    View to delete a complaint by logged-in user author of the complaint.
    To delete a complaint attribute closed must be false.
    """

    model = Complaint
    template_name = "tasksapp/complaint_confirm_delete.html"

    def dispatch(self, request, *args, **kwargs):
        complaint = self.get_object()
        if complaint.closed:
            messages.warning(self.request, "Complaint was closed. It can't be deleted")
            return HttpResponseRedirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        complaint = self.get_object()
        task = Task.objects.filter(id=complaint.task.id).first()
        return reverse("task-detail", kwargs={"pk": task.id})

    def test_func(self):
        complaint = self.get_object()
        user = self.request.user
        return user == complaint.complainant

    def handle_no_permission(self):
        redirect_url = self.get_success_url()
        return HttpResponseRedirect(redirect_url)

    def form_valid(self, form):
        """Change status of task to ON-GOING"""
        complaint = self.get_object()
        task = Task.objects.filter(id=complaint.task.id).first()
        task.status = Task.TaskStatus.ON_GOING
        task.save()
        return super().form_valid(form)
