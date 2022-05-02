#!/bin/bash

# ---------------------------------
# Expected env. variables added via kubernetes
#  with example values
#
#  STATIC_ROOT: "/dpcreator_volume/static/dist"
#  STATIC_URL: "/static/dist/"
#  UPLOADED_FILE_STORAGE_ROOT: "/dpcreator_user_data"
#
# ---------------------------------

# Switch to directory with server code, etc.
cd /code/server

# -----------------------------------------
# Run migration scripts
# -----------------------------------------
printf "\n(10) Run migration script"

# Make sure the db connection is ready...
python manage.py waitdb --seconds=10 --max_retries=20
sh -c "./migrate.sh"

printf "\n(20) Run sites script for dev.dpcreator.org"
python /code/server/manage.py loaddata opendp_apps/content_pages/fixtures/sites-dev.dpcreator.org.json

printf "\n(30) Keep only one registered dataverse"
python /code/server/manage.py set_registered_dataverse http://dev-dataverse.dpcreator.org "Dev Dataverse"

# -----------------------------------------
# Collect static files to a shared volume
#  where they are nginx accessible
# -----------------------------------------
printf "\n(40) Collect static files"

# directory that will be a shared volume
mkdir -p /dpcreator_volume/static/dist

python manage.py collectstatic --no-input

# -------------------------------------
# For deployment, re-copy static files where they can be shared
# -------------------------------------
#printf "\n(30) Copy static files to the shared volume (to be served via nginx)"
#mkdir -p /dpcreator_volume/

# -----------------------------------------
# Run Daphne server
# -----------------------------------------
printf "\n(50) Run Daphne server"
daphne -b 0.0.0.0 -p 8000 opendp_project.asgi_azure:application
