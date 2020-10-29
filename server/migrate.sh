#!/bin/sh
echo "RUNNING MIGRATIONS"
python manage.py makemigrations
python manage.py migrate
exec "$@"
