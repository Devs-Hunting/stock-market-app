from django.contrib import admin  # noqa

from .models import Offer, Payment, Task, TaskAttachment

admin.site.register([Offer, Task, TaskAttachment, Payment])
