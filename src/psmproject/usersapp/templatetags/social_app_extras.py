from allauth.socialaccount.models import SocialApp
from django import template

register = template.Library()


@register.simple_tag
def oauth2_available(provider: str):
    return SocialApp.objects.filter(provider__iexact=provider)
