from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView

from ..forms.complaint import ComplaintAttachmentForm
from ..forms.tasks import TaskAttachmentForm
from ..models import (
    Complaint,
    ComplaintAttachment,
    Solution,
    SolutionAttachment,
    Task,
    TaskAttachment,
)


class AttachmentAddView(UserPassesTestMixin, CreateView):
    url_success = None
    url_error = None
    attachment_model = None
    context_class = None

    def get_object(self):
        object_id = self.kwargs["pk"]
        try:
            return self.attachment_model.objects.get(id=object_id)
        except ObjectDoesNotExist:
            return None

    def get_success_url(self):
        object_with_adding_attachment = self.get_object()
        if object_with_adding_attachment:
            return reverse_lazy(self.url_success, kwargs={"pk": object_with_adding_attachment.id})
        return reverse_lazy(self.url_error)

    @property
    def object_with_attachments_attributes(self):
        return {
            Complaint: "complainant",
            Task: "client",
            Solution: "offer.contractor",
        }

    def test_func(self):
        obj = self.get_object()
        if obj:
            return getattr(obj, self.object_with_attachments_attributes[obj.__class__]) == self.request.user
        else:
            return False

    def handle_no_permission(self):
        user = self.request.user
        if not user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        object = self.get_object()
        if object:
            return super().get(request, *args, **kwargs)

        return HttpResponseRedirect(self.success_url)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context[self.context_class] = self.get_object()
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        form.data._mutable = True
        form.data[self.context_class] = self.get_object()
        form.data._mutable = False
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class AttachmentDeleteView(UserPassesTestMixin, DeleteView):
    """
    This view is base view for all attachment views. It is used to delete attachment.
    Only task-creator/complainant or moderator can do this.
    """

    template_name = "tasksapp/attachment_confirm_delete.html"
    url_success = None
    url_error = None
    context_class = None
    allowed_groups = [
        settings.GROUP_NAMES.get("MODERATOR"),
    ]

    @property
    def attachments_object_attributes(self):
        return {
            ComplaintAttachment: {
                "related_obj": "complaint",
                "test_func": "complainant",
            },
            TaskAttachment: {
                "related_obj": "task",
                "test_func": "client",
            },
            SolutionAttachment: {
                "related_obj": "solution",
                "test_func": "offer.contractor",
            },
        }

    def get_object_task_complaint_attachment(self):
        obj = self.get_object()
        return getattr(obj, self.attachments_object_attributes[obj.__class__]["related_obj"])

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context[self.context_class] = self.get_object_task_complaint_attachment()
        return context

    def get_success_url(self):
        object = self.get_object_task_complaint_attachment()
        if object:
            return reverse_lazy(self.url_success, kwargs={"pk": object.id})
        return reverse_lazy(self.url_error)

    def test_func(self):
        obj = self.get_object()
        object_for_attachment = self.get_object_task_complaint_attachment()
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=AttachmentDeleteView.allowed_groups).exists()
        return (
            getattr(object_for_attachment, self.attachments_object_attributes[obj.__class__]["test_func"]) == user
            or in_allowed_group
        )

    def handle_no_permission(self):
        user = self.request.user
        if not user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(self.get_success_url())


class TaskAttachmentAddView(AttachmentAddView):
    """
    This view is used to add attachment to Task. Task id must be a part of the URL.
    On GET it will display form for uploading file.
    On POST file will be validated and saved.
    """

    model = TaskAttachment
    form_class = TaskAttachmentForm
    attachment_model = Task
    url_success = "task-detail"
    url_error = "tasks-client-list"
    context_class = "task"


class TaskAttachmentDeleteView(AttachmentDeleteView):
    """
    This view is base view for all attachment views. It is used to delete attachment.
    Only task-creator/complainant or moderator can do this.
    """

    model = TaskAttachment
    url_success = "task-detail"
    url_error = "tasks-client-list"
    context_class = "task"


class ComplaintAttachmentAddView(AttachmentAddView):
    """
    This view is used to add attachment to Complaint. Complaint id must be a part of the URL.
    On GET it will display form for uploading file.
    On POST file will be validated and saved.
    """

    model = ComplaintAttachment
    form_class = ComplaintAttachmentForm
    attachment_model = Complaint
    url_success = "complaint-detail"
    url_error = "tasks-client-list"
    context_class = "complaint"


class ComplaintAttachmentDeleteView(AttachmentDeleteView):
    """
    This view is used delete attachment from Complaint. Only complaint creator or moderator can do this.
    """

    model = ComplaintAttachment
    attachment_model = Complaint
    url_success = "complaint-detail"
    url_error = "tasks-client-list"
    context_class = "complaint"


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
