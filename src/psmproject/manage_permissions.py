import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "psmproject.settings.development")
django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


def setup_groups():
    # content_type = ContentType.objects.get_for_model(Task)

    blocked_users_group, created = Group.objects.get_or_create(name="BlockedUsers")

    content_types = ContentType.objects.all()
    for content_type in content_types:
        try:
            permission = Permission.objects.get(content_type=content_type, codename="view")
        except Permission.DoesNotExist:
            permission = Permission.objects.create(
                codename="view", name="Can view {}".format(content_type.model), content_type=content_type
            )
        blocked_users_group.permissions.add(permission)


if __name__ == "__main__":
    setup_groups()
