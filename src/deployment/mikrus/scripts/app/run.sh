#!/bin/sh

set -e

python manage.py makemigrations
python manage.py migrate
python manage.py initadmin
python manage.py collectstatic --noinput
gunicorn -b 0.0.0.0:8000 psmproject.wsgi:application
