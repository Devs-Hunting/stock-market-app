from datetime import datetime

from celery import shared_task
from django.contrib.auth.models import Group
from usersapp.models import BlockedUser


@shared_task
def unblock_user(blocked_user_id):
    blocked_user = BlockedUser.objects.get(id=blocked_user_id)

    if blocked_user.blocking_end_date <= datetime.now():
        blocked_user.blocked_user.groups.remove(Group.objects.get(name="BlockedUsers"))
