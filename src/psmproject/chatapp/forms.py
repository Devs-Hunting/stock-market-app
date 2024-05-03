from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.utils.translation import gettext_lazy as _


class ChatSearchForm(forms.Form):
    contact_name = forms.CharField(required=False)

    class Meta:
        fields = ("contact_name",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.layout = Layout(
            InlineField(_("contact_name"), wrapper_class="my-2 w-25"),
        )
