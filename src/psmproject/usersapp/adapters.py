from random import randint

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, *data):
        user = super().populate_user(request, *data)
        user.username = (
            f"{user.first_name[0].lower()}{user.last_name.lower()}{randint(1000, 9999)}"
        )
        return user
