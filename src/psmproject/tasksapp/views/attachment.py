from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView

from ..forms.tasks import TaskAttachmentForm
from ..models import Task, TaskAttachment


class TaskAttachmentAddView(UserPassesTestMixin, CreateView):
    """
    This view is used to add attachment to Task. Task id must be a part of the URL.
    On GET it will display form for uploading file.
    On POST file will be validated and saved.
    """

    model = TaskAttachment
    form_class = TaskAttachmentForm

    def get_task(self):
        task_id = self.kwargs["pk"]
        try:
            return Task.objects.get(id=task_id)
        except ObjectDoesNotExist:
            return None

    def get_success_url(self):
        task = self.get_task()
        if task:
            return reverse_lazy("task-detail", kwargs={"pk": task.id})
        return reverse_lazy("tasks-client-list")

    def test_func(self):
        task = self.get_task()
        if task:
            return task.client == self.request.user
        return reverse_lazy("tasks-client-list")

    def handle_no_permission(self):
        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        task = self.get_task()
        if task:
            return super().get(request, *args, **kwargs)

        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task"] = self.get_task()
        return context

    def post(self, request, *args, **kwargs):
        """
        Set Task before validating file. Task is used to count maximal number of attachments
        """
        self.object = None
        form = self.get_form()
        form.data._mutable = True
        form.data["task"] = self.get_task()
        form.data._mutable = False
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class TaskAttachmentDeleteView(UserPassesTestMixin, DeleteView):
    """
    This view is used delete attachment from Task. Only task creator or moderator can do this.
    """

    model = TaskAttachment
    allowed_groups = [
        settings.GROUP_NAMES.get("MODERATOR"),
    ]
    template_name = "tasksapp/attachment_confirm_delete.html"

    def get_success_url(self):
        task = self.get_object().task
        if task:
            return reverse_lazy("task-detail", kwargs={"pk": task.id})
        return reverse_lazy("tasks-client-list")

    def test_func(self):
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=TaskAttachmentDeleteView.allowed_groups).exists()
        return user == self.get_object().task.client or in_allowed_group

    def handle_no_permission(self):
        redirect_url = self.get_success_url()
        return HttpResponseRedirect(redirect_url)


def download(request, pk):
    attachment = get_object_or_404(TaskAttachment, pk=pk)
    response = HttpResponse(attachment.attachment, content_type="text/plain")
    response["Content-Disposition"] = f'attachment; filename="{attachment.attachment.name}"'
    return response
