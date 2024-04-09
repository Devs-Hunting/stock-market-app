from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        if User.objects.count() == 0:
            print("Creating superuser")
            admin = User.objects.create_superuser(
                email=settings.ADMIN_EMAIL,
                username=settings.ADMIN_USER,
                password=settings.ADMIN_PASS,
            )
            admin.is_active = True
            admin.is_admin = True
            admin.save()
            print("Done")
        else:
            print("Admin accounts can only be initialized once")
