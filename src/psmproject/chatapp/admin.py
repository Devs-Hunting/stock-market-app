from chatapp.models import Chat, Message, Participant
from django.contrib import admin  # noqa

admin.site.register([Chat, Participant, Message])
