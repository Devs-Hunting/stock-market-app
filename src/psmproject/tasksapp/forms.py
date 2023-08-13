from django.forms import CharField, DateInput, HiddenInput, ModelForm, ValidationError
from django.template.defaultfilters import filesizeformat
from usersapp.helpers import skills_from_text, skills_to_text

from .models import Task, TaskAttachment


class DateInput(DateInput):
    input_type = "date"


class TaskBaseForm(ModelForm):
    template_name = "tasksapp/form_snippet.html"
    skills_as_string = CharField(required=False)

    class Meta:
        model = Task
        exclude = ["skills"]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance")
        if instance:
            skills_str_list = skills_to_text(list(instance.skills.all()))
            skills_as_string = ", ".join(skills_str_list)
            initial = kwargs.get("initial")
            initial.update({"skills_as_string": skills_as_string})
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        super().save(commit=commit)
        if self.instance.id:
            self.instance.skills.clear()
            skills_as_string = self.cleaned_data.get("skills_as_string")
            if skills_as_string and len(skills_as_string) > 0:
                skills_str_list = self.cleaned_data["skills_as_string"].split(", ")
                skills = skills_from_text(skills_str_list)
                self.instance.skills.add(*skills)
        return self.instance


class TaskForm(TaskBaseForm):
    class Meta:
        model = Task
        exclude = ["client", "status", "skills"]
        widgets = {"realization_time": DateInput()}


class UpdateTaskForm(TaskBaseForm):
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
