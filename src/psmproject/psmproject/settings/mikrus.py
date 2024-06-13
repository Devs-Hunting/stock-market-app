from .base import *  # noqa

DEBUG = False

TEST_HOST = f"http://localhost:{env.int('IP4_PORT')}"
CSRF_TRUSTED_ORIGINS = [env.str("HOST_NAME"), TEST_HOST]

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

MEDIA_URL = f"{env.str('HOST_NAME')}/media/"

EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
SENDGRID_API_KEY = env.str("SENDGRID_API_KEY")

ADMIN_USER = env.str("ADMIN_USER")
ADMIN_EMAIL = env.str("ADMIN_EMAIL")
ADMIN_PASS = env.str("ADMIN_PASS")
