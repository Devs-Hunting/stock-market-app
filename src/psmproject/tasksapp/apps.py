from django.apps import AppConfig


class TasksappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tasksapp"

    def ready(self):
        import chatapp.signals  # noqa

        from . import signals  # noqa
