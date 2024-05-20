from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Offer
from .common import InlineCrispyForm


class TaskSearchForm(InlineCrispyForm):
    query = forms.CharField(label=_("Search"), max_length=100)
    min_days_to_complete = forms.IntegerField(label=_("Min days to complete"), min_value=1)
    max_days_to_complete = forms.IntegerField(label=_("Min days to complete"), min_value=1)
    budget = forms.DecimalField(label=_("Budget"), max_digits=6, decimal_places=2)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.keys():
            self.fields[field].required = False

    #     self.helper = FormHelper()
    #     self.helper.disable_csrf = True
    #     self.helper.form_tag = False
    #     self.helper.form_class = "form-inline"
    #     self.helper.field_template = "bootstrap5/layout/inline_field.html"
    #     self.helper.layout = Layout(
    #         Div(
    #             InlineField("query", wrapper_class="col"),
    #             InlineField("realization_time", wrapper_class="col"),
    #             InlineField("budget", wrapper_class="col"),
    #             css_class="row mb-3 align-items-center",
    #         )
    #     )


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["description", "days_to_complete", "budget"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["days_to_complete"].widget.attrs["min"] = 1


class OfferModeratorForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["description"]


class OfferSearchForm(InlineCrispyForm):
    query = forms.CharField(label=_("Search"), max_length=100, min_length=3, required=False)
    accepted = forms.BooleanField(required=False)
