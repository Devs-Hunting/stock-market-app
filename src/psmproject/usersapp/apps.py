from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UsersappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "usersapp"

    def ready(self):
        from .signals import create_groups

        post_migrate.connect(create_groups, sender=self)
