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
    """Django command to create dummy data"""

    @disable_signals_for_loaddata
    def handle(self, *args, **kwargs):
        """Entrypoint for command."""
        self.stdout.write("Checking if dummy data already exist...")
        users = User.objects.all()
        if not users.filter(is_superuser=False) and users.count() < 2:
            self.stdout.write("Importing data from fixtures")
            apps = ["usersapp", "tasksapp", "chatapp"]
            fixture_full_paths = [f"{app}/fixtures/*.json" for app in apps]
            os.system(f"python manage.py loaddata {' '.join(fixture_full_paths)}")

            for user in users.filter(is_superuser=False):
                user.set_password(user.password)
                user.save()

            self.stdout.write(self.style.SUCCESS("Fixtures loaded."))

        else:
            self.stdout.write(self.style.ERROR("Data already exist in database, not able to load dummy data."))
