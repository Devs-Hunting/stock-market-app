from django import forms

from .models import Offer


class DateInput(forms.DateInput):
    input_type = "date"


class TaskSearchForm(forms.Form):
    template_name = "offerapp/form_snippet_horizontal.html"

    query = forms.CharField(label="Search", max_length=100, required=False)
    realization_time = forms.DateField(widget=DateInput(), required=False)
    budget = forms.DecimalField(max_digits=6, decimal_places=2, required=False)


class OfferForm(forms.ModelForm):
    template_name = "offerapp/form_snippet.html"

    class Meta:
        model = Offer
        fields = ["description", "realization_time", "budget"]
        widgets = {"realization_time": DateInput()}


class OfferModeratorForm(forms.ModelForm):
    template_name = "offerapp/form_snippet.html"

    class Meta:
        model = Offer
        fields = ["description"]


class OfferSearchForm(forms.Form):
    template_name = "offerapp/form_snippet_horizontal.html"

    query = forms.CharField(label="Search", max_length=100, min_length=3, required=False)
    accepted = forms.BooleanField(required=False)
