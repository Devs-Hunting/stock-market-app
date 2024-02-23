from celery import shared_task
from celery.exceptions import SoftTimeLimitExceeded
from django.conf import settings
from django.core.mail import send_mail


@shared_task(time_limit=240)
def send_mail_task(subject, message, recipient):
    try:
        send_mail(subject=subject, message=message, from_email=settings.EMAIL_SENDER, recipient_list=[recipient])
    except SoftTimeLimitExceeded:
        pass
