from django import forms
from django.contrib.auth.models import User
from django.forms import DateInput, ModelForm

from .models import BlockedUser

# from .models import User


class CustomSignUpForm(forms.Form):
    first_name = User._meta.get_field("first_name").formfield(
        widget=forms.TextInput(attrs={"placeholder": "Enter your first name"})
    )
    last_name = User._meta.get_field("last_name").formfield(
        widget=forms.TextInput(attrs={"placeholder": "Enter your last name"})
    )

    def signup(self, request, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()


class BlockUserForm(ModelForm):
    class Meta:
        model = BlockedUser
        exclude = ["blocking_user", "blocking_start_date"]
        widgets = {
            "blocking_end_date": DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "full_blocking": forms.CheckboxInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        full_blocking = cleaned_data.get("full_blocking")
        blocking_end_date = cleaned_data.get("blocking_end_date")

        if full_blocking and blocking_end_date:
            raise forms.ValidationError("For full blocking user, leave blocking end date empty")

        return cleaned_data
