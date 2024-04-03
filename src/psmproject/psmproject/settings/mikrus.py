import os

from .base import *  # noqa

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = False
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": os.environ["DB_ENGINE"],
        "NAME": os.environ["DB_DB"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"],
        "PORT": os.environ["DB_PORT"],
    }
}

CSRF_TRUSTED_ORIGINS = [os.environ["HOST_NAME"], os.environ["TEST_HOST"]]

CELERY_BROKER_URL = os.environ["CELERY_BROKER_URL"]
CELERY_RESULT_BACKEND = os.environ["CELERY_RESULT_BACKEND"]

MEDIA_URL = os.environ["HOST_NAME"] + "/media/"

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
DEFAULT_FROM_EMAIL = os.environ["DEFAULT_FROM_EMAIL"]
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@admin.com")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "pass")
