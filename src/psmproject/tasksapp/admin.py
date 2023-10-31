from django.contrib import admin  # noqa

from .models import Offer, Task, TaskAttachment

admin.site.register([Offer, Task, TaskAttachment])
