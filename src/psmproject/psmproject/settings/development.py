from .base import *  # noqa

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_SENDER = "from@example.com"

ADMIN_USER = env.str("ADMIN_USER", "admin")
ADMIN_EMAIL = env.str("ADMIN_EMAIL", "admin@admin.com")
ADMIN_PASS = env.str("ADMIN_PASS", "pass")
