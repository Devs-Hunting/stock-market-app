from django.contrib import admin  # noqa
from usersapp.models import Notification, Rating, Skill, UserProfile

admin.site.register([Skill, Notification, UserProfile, Rating])
