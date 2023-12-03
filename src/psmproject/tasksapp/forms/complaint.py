from django import forms
from django.template.defaultfilters import filesizeformat

from ..models import Complaint, ComplaintAttachment


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["content"]


class ComplaintAttachmentForm(forms.ModelForm):
    template_name = "tasksapp/form_snippet.html"

    class Meta:
        model = ComplaintAttachment
        fields = "__all__"
        widgets = {"complaint": forms.HiddenInput()}

    def clean_attachment(self):
        """
        Custom clean method to verify attachment file properties. Conditions are defined in a model.
        Properties checked:
        1. File type
        2. File size
        """
        attachment = self.cleaned_data["attachment"]
        if attachment.content_type in ComplaintAttachment.CONTENT_TYPES:
            if attachment.size > ComplaintAttachment.MAX_UPLOAD_SIZE:
                error_message = f"File too big. Max file size: {filesizeformat(ComplaintAttachment.MAX_UPLOAD_SIZE)}"
                raise forms.ValidationError(error_message)
        else:
            raise forms.ValidationError("File type is not supported")
        return attachment
