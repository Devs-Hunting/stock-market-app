from django.forms import DateInput, HiddenInput, ModelForm

from .models import Task, TaskAttachment


class DateInput(DateInput):
    input_type = "date"


class TaskForm(ModelForm):
    template_name = "tasksapp/form_snippet.html"

    class Meta:
        model = Task
        exclude = ["client", "status"]
        widgets = {"realization_time": DateInput()}


class UpdateTaskForm(ModelForm):
    template_name = "tasksapp/form_snippet.html"

    class Meta:
        model = Task
        exclude = ["client"]
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
