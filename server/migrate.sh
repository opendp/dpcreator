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
echo

echo "-----------------------"
echo "| Create Super User   |"
echo "-----------------------"
python /code/server/manage.py create_superuser
echo "username: admin"
echo "password: admin"
exec "$@"
echo

echo "-----------------------"
echo "| Create Social App   |"
echo "-----------------------"
python /code/server/manage.py create_social_app
exec "$@"
echo

echo "-----------------------"
echo "| Load fixtures       |"
echo "| (for dev)           |"
echo "-----------------------"
python /code/server/manage.py loaddata opendp_apps/dataverses/fixtures/admin_emailaddress.json
python /code/server/manage.py loaddata opendp_apps/dataverses/fixtures/terms.json
python /code/server/manage.py loaddata opendp_apps/dataverses/fixtures/test_dataverses_01.json
# python /code/server/manage.py loaddata opendp_apps/dataverses/fixtures/test_user_emailaddress.json
python /code/server/manage.py loaddata opendp_apps/banner_messages/fixtures/*.json
#  opendp_apps/banner_messages/fixtures/*.json
#   opendp_apps/dataset/fixtures/*.json
exec "$@"
echo
