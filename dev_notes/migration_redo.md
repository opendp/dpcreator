
### Still early in the dev process clearing migrations

```
cd server
rm -rf opendp_apps/analysis/migrations \
    opendp_apps/communication/migrations \
    opendp_apps/content_pages/migrations \
    opendp_apps/dataset/migrations \
    opendp_apps/dataverses/migrations \
    opendp_apps/profiler/migrations \
    opendp_apps/terms_of_access/migrations \
    opendp_apps/user/migrations 


python manage.py makemigrations dataverses user dataset terms_of_access content_pages analysis profiler
# communication

export DJANGO_SETTINGS_MODULE=opendp_project.settings.development_test

python manage.py makemigrations dataset
```