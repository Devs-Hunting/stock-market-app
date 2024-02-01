#!/bin/sh

set -e

python manage.py makemigrations
python manage.py migrate
<<<<<<< HEAD
# python manage.py load_fixtures
=======
python manage.py load_fixtures
>>>>>>> 753fcd2bf0453c0caab684528a5a7e21ecfc5fab
# python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
