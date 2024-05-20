from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _

from ..models import Complaint, ComplaintAttachment
from .common import DateInput, InlineCrispyForm


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["content"]


class ComplaintSearchForm(InlineCrispyForm):
    query = forms.CharField(label=_("Search"), max_length=100, min_length=3, required=False)
    taken = forms.BooleanField(required=False)
    closed = forms.BooleanField(required=False)
    date_start = forms.DateField(widget=DateInput(), required=False)
    date_end = forms.DateField(widget=DateInput(), required=False)


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
                error_message = _("File too big. Max file size: ") + filesizeformat(ComplaintAttachment.MAX_UPLOAD_SIZE)
                raise forms.ValidationError(error_message)
        else:
            raise forms.ValidationError("File type is not supported")
        return attachment
