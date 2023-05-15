
## Remove/rebuild migrations

```
cd server

import os
from os.path import isdir, isfile, join
import shutil

base_dir = 'opendp_apps'
app_names = []
for app_name in os.listdir(base_dir):
    if app_name[0] in ['_', '.']:
        continue
    dir_to_check = join(base_dir, app_name, 'migrations')
    print(f'checking: {dir_to_check}')
    app_names.append(app_name)
    if isdir(dir_to_check):
        shutil.rmtree(dir_to_check)
        print(f'Deleted: {dir_to_check}')
        
for app_name in app_names:
    print(f'python manage.py makemigrations {app_name} --settings=opendp_project.settings.development_test')
```

- Initial output:
```
python manage.py test --settings=opendp_project.settings.development_test

python manage.py makemigrations model_helpers --settings=opendp_project.settings.development_test
python manage.py makemigrations content_pages --settings=opendp_project.settings.development_test
python manage.py makemigrations dataverses --settings=opendp_project.settings.development_test
python manage.py makemigrations user --settings=opendp_project.settings.development_test
python manage.py makemigrations dataset --settings=opendp_project.settings.development_test
python manage.py makemigrations analysis --settings=opendp_project.settings.development_test
python manage.py makemigrations terms_of_access --settings=opendp_project.settings.development_test

python manage.py makemigrations banner_messages --settings=opendp_project.settings.development_test
python manage.py makemigrations cypress_utils --settings=opendp_project.settings.development_test
python manage.py makemigrations utils --settings=opendp_project.settings.development_test
python manage.py makemigrations dp_reports --settings=opendp_project.settings.development_test
python manage.py makemigrations async_messages --settings=opendp_project.settings.development_test
python manage.py makemigrations profiler --settings=opendp_project.settings.development_test
```


### Run a detached postgres container

```
docker run \
  --rm \
  --name postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  postgres:12.14

#   -v /Users/ramanprasad/Documents/web-test-dbs:/var/lib/postgresql/data \
```


```
docker exec -it postgres /bin/bash
createuser  -U postgres postgres 
createdb  -U postgres pathway_db --owner postgres
```

### Manifest Test Params (old)

Incoming Dataverse link

```
python manage.py dumpdata --indent=4 dataverses.manifesttestparams > opendp_apps/dataverses/fixtures/test_manifest_params_04.json
```