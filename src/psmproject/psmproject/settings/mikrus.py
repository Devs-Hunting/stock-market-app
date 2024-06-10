import os

from .base import *  # noqa

DEBUG = False

TEST_HOST = f"http://localhost:{os.environ.get('IP4_PORT')}"
CSRF_TRUSTED_ORIGINS = [os.environ.get("HOST_NAME"), TEST_HOST]

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

MEDIA_URL = os.environ.get("HOST_NAME") + "/media/"

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")

ADMIN_USER = os.environ.get("ADMIN_USER")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASS = os.environ.get("ADMIN_PASS")
