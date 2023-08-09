from django.forms import DateInput, HiddenInput, ModelForm, ValidationError
from django.template.defaultfilters import filesizeformat

from .models import Task, TaskAttachment


class DateInput(DateInput):
    input_type = "date"


class TaskForm(ModelForm):
    template_name = "tasksapp/form_snippet.html"

    class Meta:
        model = Task
        exclude = ["client", "status", "skills"]
        widgets = {"realization_time": DateInput()}


class UpdateTaskForm(ModelForm):
    template_name = "tasksapp/form_snippet.html"

    class Meta:
        model = Task
        exclude = ["client", "skills"]
        widgets = {"realization_time": DateInput()}


class ModeratorUpdateTaskForm(ModelForm):
    template_name = "tasksapp/form_snippet.html"

    class Meta:
        model = Task
        exclude = ["client", "budget", "realization_time"]


class TaskAttachmentForm(ModelForm):
    template_name = "tasksapp/form_snippet.html"

    class Meta:
        model = TaskAttachment
        fields = "__all__"
        widgets = {"task": HiddenInput()}

    def clean_attachment(self):
        """
        Custom clean method to verify attachment file properties. Conditions are defined in a model.
        Properties checked:
        1. File type
        2. File size
        """
        attachment = self.cleaned_data["attachment"]
        if attachment.content_type in TaskAttachment.CONTENT_TYPES:
            if attachment.size > TaskAttachment.MAX_UPLOAD_SIZE:
                error_message = f"File too big. Max file size: {filesizeformat(TaskAttachment.MAX_UPLOAD_SIZE)}"
                raise ValidationError(error_message)
        else:
            raise ValidationError("File type is not supported")
        return attachment
