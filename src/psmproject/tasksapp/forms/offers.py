from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django import forms

from ..models import Offer


class DateInput(forms.DateInput):
    input_type = "date"


class TaskSearchForm(forms.Form):

    query = forms.CharField(label="Search", max_length=100, required=False)
    realization_time = forms.DateField(widget=DateInput(), required=False)
    budget = forms.DecimalField(max_digits=6, decimal_places=2, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_class = "form-inline"
        self.helper.field_template = "bootstrap5/layout/inline_field.html"
        self.helper.layout = Layout(
            Div(
                InlineField("query", wrapper_class="col"),
                InlineField("realization_time", wrapper_class="col"),
                InlineField("budget", wrapper_class="col"),
                css_class="row mb-3 align-items-center",
            )
        )


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["description", "realization_time", "budget"]
        widgets = {"realization_time": DateInput()}


class OfferModeratorForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["description"]


class OfferSearchForm(forms.Form):

    query = forms.CharField(label="Search", max_length=100, min_length=3, required=False)
    accepted = forms.BooleanField(required=False)
