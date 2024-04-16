#!/bin/sh

set -e

python manage.py makemigrations
python manage.py migrate
python manage.py initadmin
python manage.py collectstatic --noinput
daphne -b 0.0.0.0 -p 8000 psmproject.asgi:application
