from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def post_login(sender, user, request, **kwargs):
    request.session["role"] = user.groups.all()[0].id
    request.session["role_name"] = user.groups.all()[0].name
