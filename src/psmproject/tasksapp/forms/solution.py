from django import forms
from django.template.defaultfilters import filesizeformat

from ..models import Solution, SolutionAttachment
from .common import InlineCrispyForm


class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ["description"]


class SolutionModeratorForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ["description"]


class SolutionSearchForm(InlineCrispyForm):
    query = forms.CharField(label="Search", max_length=100, min_length=3, required=False)
    accepted = forms.BooleanField(required=False)


class SolutionAttachmentForm(forms.Form):
    template_name = "tasksapp/form_snippet.html"
    attachment = forms.FileField(label="Attachment", required=False)
    # class Meta:
    #    model = SolutionAttachment
    #    fields = ["attachment"]

    def clean_attachment(self):
        """
        Custom clean method to verify attachment file properties. Conditions are defined in a model.
        Properties checked:
        1. File type
        2. File size
        """
        attachment = self.cleaned_data["attachment"]
        if attachment.content_type in SolutionAttachment.CONTENT_TYPES:
            if attachment.size > SolutionAttachment.MAX_UPLOAD_SIZE:
                error_message = f"File too big. Max file size: {filesizeformat(SolutionAttachment.MAX_UPLOAD_SIZE)}"
                raise forms.ValidationError(error_message)
        else:
            raise forms.ValidationError("File type is not supported")
        return attachment
