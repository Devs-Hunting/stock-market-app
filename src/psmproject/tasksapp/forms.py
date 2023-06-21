from django.forms import ModelForm

from .models import TaskAttachment


class TaskAttachmentForm(ModelForm):
    template_name = "tasksapp/form_snippet.html"

    class Meta:
        model = TaskAttachment
        exclude = ["task"]
