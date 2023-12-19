from typing import Any

from django.conf import settings
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView

from ..forms.complaint import ComplaintAttachmentForm
from ..forms.solution import SolutionAttachmentForm
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
            return getattr(obj, self.object_with_attachments_attributes[type(obj)]) == self.request.user
        else:
            return False

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
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

    def get_related_object(self):
        obj = self.get_object()
        return getattr(obj, self.attachments_object_attributes[type(obj)]["related_obj"])

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context[self.context_class] = self.get_related_object()
        return context

    def get_success_url(self):
        object = self.get_related_object()
        if object:
            return reverse_lazy(self.url_success, kwargs={"pk": object.id})
        return reverse_lazy(self.url_error)

    def test_func(self):
        obj = self.get_object()
        object_for_attachment = self.get_related_object()
        user = self.request.user
        in_allowed_group = user.groups.filter(name__in=AttachmentDeleteView.allowed_groups).exists()
        return (
            getattr(object_for_attachment, self.attachments_object_attributes[type(obj)]["test_func"]) == user
            or in_allowed_group
        )

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
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


class SolutionAttachmentAddView(AttachmentAddView):
    """
    This view is used to add attachment to Solution. Solution id must be a part of the URL.
    On GET it will display form for uploading file. On POST file will be validated and saved.
    """

    model = SolutionAttachment
    form_class = SolutionAttachmentForm
    attachment_model = Solution
    url_success = "solution-detail"
    url_error = "tasks-contractor-list"
    context_class = "solution"


class SolutionAttachmentDeleteView(AttachmentDeleteView):
    """
    This view is used delete attachment from Solution. Only solution creator or moderator can do this.
    """

    model = SolutionAttachment
    attachment_model = Solution
    url_success = "solution-detail"
    url_error = "tasks-contractor-list"
    context_class = "solution"


class DownloadAttachmentView(UserPassesTestMixin, DetailView):
    """
    Class based view for downloading attachments for Complaint, Task, Solution.
    """

    model = None
    url_success = None
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

    def get_related_object(self):
        obj = self.get_object()
        return getattr(obj, self.attachments_object_attributes[type(obj)]["related_obj"])

    def get_success_url(self):
        obj = self.get_object()
        if obj:
            return reverse_lazy(
                self.url_success,
                kwargs={"pk": self.get_related_object().id},
            )
        return reverse_lazy("profile")

    def is_user_in_allowed_group(self):
        return self.request.user.groups.filter(name__in=self.allowed_groups).exists()

    def is_user_authorized(self, obj):
        related_obj = self.get_related_object()
        test_attr = self.attachments_object_attributes[type(obj)]["test_func"]
        return getattr(related_obj, test_attr) == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        attachment = self.get_object()
        response = HttpResponse(attachment.attachment, content_type="text/plain")
        response["Content-Disposition"] = f'attachment; filename="{attachment.attachment.name}"'
        return response


class TaskDownloadAttachmentView(DownloadAttachmentView):
    """
    This view is used to download attachment from Task.
    Everyone can download attachment from task.
    """

    model = TaskAttachment
    url_success = "task-detail"

    def test_func(self):
        return True


class ComplaintDownloadAttachmentView(DownloadAttachmentView):
    """
    This view is used to download attachment from Complaint.
    Attachment can be downloaded by complainant, client or moderator.
    """

    model = ComplaintAttachment
    url_success = "complaint-detail"

    def test_func(self):
        obj = self.get_object()
        object_for_attachment = self.get_related_object()
        return (
            self.is_user_in_allowed_group()
            or self.is_user_authorized(obj)
            or self.request.user
            in [object_for_attachment.task.client, object_for_attachment.task.selected_offer.contractor]
        )


class SolutionDownloadAttachmentView(DownloadAttachmentView):
    """
    This view is used to download attachment from Solution.
    Solution can be downloaded by client, contractor or moderator.
    """

    model = SolutionAttachment
    url_success = "solution-detail"

    def test_func(self):
        obj = self.get_object()
        object_for_attachment = self.get_related_object()
        return (
            self.is_user_in_allowed_group()
            or self.is_user_authorized(obj)
            or self.request.user == object_for_attachment.task.client
        )
