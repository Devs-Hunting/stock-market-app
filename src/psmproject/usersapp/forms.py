from django import forms
from django.contrib.auth.models import User
from django.forms import DateInput, ModelForm
from django.utils.translation import gettext_lazy as _

from .models import BlockedUser

# from .models import User


class CustomSignUpForm(forms.Form):
    first_name_placeholder = _("Enter your first name")
    first_name = User._meta.get_field("first_name").formfield(
        widget=forms.TextInput(attrs={"placeholder": first_name_placeholder})
    )
    last_name_placeholder = _("Enter your last name")
    last_name = User._meta.get_field("last_name").formfield(
        widget=forms.TextInput(attrs={"placeholder": last_name_placeholder})
    )

    def signup(self, request, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()


class BlockUserForm(ModelForm):
    class Meta:
        model = BlockedUser
        exclude = ["blocking_user", "blocking_start_date"]
        widgets = {"blocking_end_date": DateInput(format="%Y-%m-%d", attrs={"type": "date"})}
