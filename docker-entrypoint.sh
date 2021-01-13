#!/bin/bash
echo ":::::::Makemigragions"
python manage.py makemigrations
python manage.py migrate

echo ":::::::Collect static files"
python manage.py collectstatic --noinput

echo ":::::::Run gunicorn"
gunicorn -b 0:4000 -w 2 isaac_project.wsgi:application
