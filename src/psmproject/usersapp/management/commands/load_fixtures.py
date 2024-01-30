"""
Django command to create a SuperUser and dummy data
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """Django command to create a super user and add dummy data"""

    help = "Create a new superuser"

    def handle(self, *args, **kwargs):
        """Entrypoint for command."""
        self.stdout.write("Checkig for superuser")
        if not User.objects.filter(is_superuser=True):
            self.stdout.write("Importing data from fixtures")
            os.system("python manage.py loaddata users skills tasks")
            for user in User.objects.all():
                user.set_password(user.password)
                user.save()
        else:
            self.stdout.write(self.style.SUCCESS("SuperUser exists"))
