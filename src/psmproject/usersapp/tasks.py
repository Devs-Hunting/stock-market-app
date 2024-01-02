from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import Group
from usersapp.models import BlockedUser

BLOCKED_USER_GROUP = Group.objects.get(name=settings.GROUP_NAMES.get("BLOCKED_USER"))


@shared_task
def unblock_users():
    for user in BLOCKED_USER_GROUP.user_set.all():
        active_ban_exists = BlockedUser.objects.filter(blocked_user=user, blocking_end_date__gt=datetime.now()).exists()

        if not active_ban_exists:
            BLOCKED_USER_GROUP.user_set.remove(user)
