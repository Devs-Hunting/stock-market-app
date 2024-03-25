#!/bin/sh

set -e

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn tkbproj.wsgi:application --bind 0.0.0.0:8000
