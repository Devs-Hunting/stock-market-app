from crispy_forms.bootstrap import InlineField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Layout
from django import forms


class InlineCrispyForm(forms.Form):
    def create_layout(self):
        field_objects = [InlineField(field, wrapper_class="col") for field in self.fields]
        layout = Layout(
            Div(
                *field_objects,
                css_class="row mb-3 align-items-center",
            )
        )
        return layout

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.form_class = "form-inline"
        self.helper.field_template = "bootstrap5/layout/inline_field.html"
        self.helper.layout = self.create_layout()
