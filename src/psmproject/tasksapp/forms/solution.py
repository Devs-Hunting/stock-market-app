from django import forms

from ..models import Solution


class SolutionForm(forms.ModelForm):
    class Meta:
        model = Solution
        fields = ["description"]
