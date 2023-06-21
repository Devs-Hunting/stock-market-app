from django.contrib import admin  # noqa
from tasksapp.models import Task, TaskAttachment

admin.site.register([Task, TaskAttachment])
