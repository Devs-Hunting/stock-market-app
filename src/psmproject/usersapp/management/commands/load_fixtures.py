"""
Django command to create a SuperUser and dummy data
"""

import os
from functools import wraps

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


def disable_signals_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get("raw"):
            return
        signal_handler(*args, **kwargs)

    return wrapper


class Command(BaseCommand):
    """Django command to create a super user and add dummy data"""

    help = "Create a new superuser"

    @disable_signals_for_loaddata
    def handle(self, *args, **kwargs):
        """Entrypoint for command."""
        self.stdout.write("Checking for superuser")
        if not User.objects.filter(is_superuser=True):
            self.stdout.write("Importing data from fixtures")
            fixture_files = [
                "001-groups",
                "002-users",
                "003-skills",
                "004-user-profiles",
                "001-tasks",
                "002-solutions",
                "003-offers",
                "004-tasks-select-offers",
                "005-complaints",
                "001-chats",
                "002-participants",
                "003-messages",
            ]

            os.system("python manage.py loaddata " + " ".join(fixture_files))
            for user in User.objects.all():
                user.set_password(user.password)
                user.save()
        else:
            self.stdout.write(self.style.SUCCESS("SuperUser exists"))
