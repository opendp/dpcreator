#!/bin/sh
echo "-----------------------"
echo "| Creating Migrations |"
echo "-----------------------"
python /code/server/manage.py makemigrations
echo

echo "-----------------------"
echo "| Running Migrations  |"
echo "-----------------------"
python /code/server/manage.py migrate
exec "$@"
