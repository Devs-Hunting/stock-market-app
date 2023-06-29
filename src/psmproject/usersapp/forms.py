from django import forms

from .models import User


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
