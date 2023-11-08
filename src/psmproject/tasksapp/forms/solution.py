from django import forms

from ..models import Solution
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
