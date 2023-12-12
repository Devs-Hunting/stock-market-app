from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView

from ..forms.tasks import TaskAttachmentForm
from ..models import ComplaintAttachment, SolutionAttachment, Task, TaskAttachment


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


class DownloadAttachmentView(UserPassesTestMixin, DetailView):
    """
    Class based view for downloading attachments for Complaint, Task, Solution.
    """

    allowed_groups = [
        settings.GROUP_NAMES.get("MODERATOR"),
    ]

    @property
    def attachments_object_attributes(self):
        return {
            ComplaintAttachment: {
                "related_obj": "complaint",
                "test_func": "complainant",
                "url_success": "complaint-detail",
            },
            TaskAttachment: {
                "related_obj": "task",
                "test_func": "client",
                "url_success": "task-detail",
            },
            SolutionAttachment: {
                "related_obj": "solution",
                "test_func": "offer.contractor",
                "url_success": "solution-detail",
            },
        }

    def get_object_task_complaint_attachment(self):
        obj = self.get_object()
        return getattr(obj, self.attachments_object_attributes[obj.__class__]["related_obj"])

    def get_success_url(self):
        obj = self.get_object()
        object_for_attachment = self.get_object_task_complaint_attachment()
        if obj:
            return reverse_lazy(
                getattr(obj, self.attachments_object_attributes[obj.__class__]["success_url"]),
                kwargs={"pk": object_for_attachment.id},
            )
        return reverse_lazy("profile")

    def test_func(self):
        obj = self.get_object()
        object_for_attachment = self.get_object_task_complaint_attachment()
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=DownloadAttachmentView.allowed_groups).exists()
        return (
            getattr(object_for_attachment, self.attachments_object_attributes[obj.__class__]["test_func"]) == user
            or in_allowed_group
        )

    def handle_no_permission(self):
        user = self.request.user
        if not user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(self.get_success_url())

    def download(self, request, *args, **kwargs):
        attachment = self.get_object()
        response = HttpResponse(attachment.attachment, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{attachment.attachment.name}"'
        return response
