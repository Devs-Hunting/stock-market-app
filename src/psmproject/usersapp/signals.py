from django.conf import settings
from django.contrib.auth.models import Group


def create_groups(sender, **kwargs):
    for group in settings.GROUP_NAMES:
        Group.objects.get_or_create(name=settings.GROUP_NAMES.get(group))
