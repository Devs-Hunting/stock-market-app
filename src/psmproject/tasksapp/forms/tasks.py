from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django.forms import (
    CharField,
    DateInput,
    Form,
    HiddenInput,
    ModelForm,
    ValidationError,
)
from django.template.defaultfilters import filesizeformat

from ..models import Task, TaskAttachment


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
        fields = ["title", "description"]


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


class TaskSearchModeratorForm(Form):
    query = CharField(label="Title, description", max_length=100, min_length=3, required=False)
    username = CharField(label="Username", max_length=100, min_length=3, required=False)

    def create_layout(self):
        field_objects = [InlineField(field, wrapper_class="col") for field in self.fields]
        layout = Layout(
            Div(
                *field_objects,
                css_class="row mb-3 align-items-center",
            )
        )
        return layout

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = "form-inline"
        self.helper.field_template = "bootstrap5/layout/inline_field.html"
        self.helper.layout = self.create_layout()
