from django import forms


class DateInput(forms.DateInput):
    input_type = "date"


class TaskSearchForm(forms.Form):
    template_name = "offerapp/form_snippet_horizontal.html"

    query = forms.CharField(label="Search", max_length=100, required=False)
    realization_time = forms.DateField(widget=DateInput(), required=False)
    budget = forms.DecimalField(max_digits=6, decimal_places=2, required=False)
