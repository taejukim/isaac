#!/bin/bash
echo ":::::::Makemigragions"
python manage.py makemigrations
python manage.py migrate

echo ":::::::Collect static files"
python manage.py collectstatic --noinput

echo ":::::::Add Crontab job"
crontab <<< "# new crontab"
python manage.py crontab add
python manage.py crontab show

echo ":::::::Run gunicorn"
gunicorn -b 0:4000 -w 2 isaac_project.wsgi:application
