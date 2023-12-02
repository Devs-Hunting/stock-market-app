from datetime import datetime

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import Group
from usersapp.models import BlockedUser

BLOCKED_USER_GROUP = Group.objects.get(name=settings.GROUP_NAMES.get("BLOCKED_USER"))


@shared_task
def unblock_user(blocked_user_id):
    blocked_user = BlockedUser.objects.get(id=blocked_user_id)

    if blocked_user.blocking_end_date <= datetime.now():
        blocked_user.blocked_user.groups.remove(BLOCKED_USER_GROUP)
