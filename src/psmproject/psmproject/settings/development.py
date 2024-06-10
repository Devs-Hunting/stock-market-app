from .base import *  # noqa

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_SENDER = "from@example.com"

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@admin.com")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "pass")
