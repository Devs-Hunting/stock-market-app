from allauth.account.models import EmailAddress
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser=True):
            self.stdout.write("Creating superuser")
            admin = User.objects.create_superuser(
                email=settings.ADMIN_EMAIL,
                username=settings.ADMIN_USER,
                password=settings.ADMIN_PASS,
            )
            admin.is_active = True
            admin.is_admin = True
            admin.save()
            EmailAddress.objects.create(user=admin, email=admin.email, verified=True, primary=True)
            self.stdout.write(self.style.SUCCESS("Done"))
        else:
            self.stdout.write(self.style.ERROR("Admin accounts can only be initialized once"))
