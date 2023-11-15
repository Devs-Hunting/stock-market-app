from django import forms

from ..models import Complaint
from .common import DateInput, InlineCrispyForm


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["content"]


class ComplaintSearchForm(InlineCrispyForm):
    query = forms.CharField(label="Search", max_length=100, min_length=3, required=False)
    taken = forms.BooleanField(required=False)
    closed = forms.BooleanField(required=False)
    date_start = forms.DateField(widget=DateInput(), required=False)
    date_end = forms.DateField(widget=DateInput(), required=False)
