from django.apps import AppConfig

# from django.conf import settings


class UsersappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "usersapp"

    # def ready(self):
    #     from django.contrib.auth.models import Group
    #
    #     for group in settings.GROUP_NAMES:
    #         Group.objects.get_or_create(name=settings.GROUP_NAMES.get(group))
