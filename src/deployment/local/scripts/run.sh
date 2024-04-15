#!/bin/sh

set -e

python manage.py makemigrations
python manage.py migrate
python manage.py load_fixtures
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
