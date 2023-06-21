from django.contrib import admin  # noqa
from usersapp.models import Notification, Rating, Skill, User, UserProfile

admin.site.register([Skill, User, Notification, UserProfile, Rating])
