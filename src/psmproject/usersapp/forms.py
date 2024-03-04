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
        fields = ["blocked_user", "blocking_user", "reason", "blocking_end_date"]
        # exclude = ["blocking_user", "blocking_start_date"]
        widgets = {"blocking_end_date": DateInput()}

    # blocked_user = forms.ModelChoiceField(
    #    queryset=User.objects.all(), widget=forms.Select
    # )
