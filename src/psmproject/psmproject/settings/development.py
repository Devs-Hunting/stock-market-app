from .base import *  # noqa

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_SENDER = "from@example.com"

URL_BASE = "http://127.0.0.1:8000/"

ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@admin.com")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "pass")

# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "handlers": {
#         "console": {
#             "class": "logging.StreamHandler",
#         },
#     },
#     "root": {
#         "handlers": ["console"],
#         "level": "INFO",
#     },
# }
