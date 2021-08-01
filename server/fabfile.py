"""Convenience commands"""
import os, sys
from os.path import abspath, join, isdir
import random
import string
from fabric import task
from invoke import run as fab_local
import django

# ----------------------------------------------------
# Add this directory to the python system path
# ----------------------------------------------------
FAB_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(FAB_BASE_DIR)

# ----------------------------------------------------
# Set the DJANGO_SETTINGS_MODULE, if it's not already
# ----------------------------------------------------
KEY_DJANGO_SETTINGS_MODULE = 'DJANGO_SETTINGS_MODULE'
KEY_DEV_SETTINGS = 'opendp_project.settings.development'
os.environ.setdefault(KEY_DJANGO_SETTINGS_MODULE,
                      KEY_DEV_SETTINGS)

# ----------------------------------------------------
# Django setup
# ----------------------------------------------------
try:
    django.setup()
except Exception as e:
    print("WARNING: Can't configure Django. %s" % e)


@task
def init_db(context):
    """Initialize the django database (if needed)"""
    export_cmd = get_export_db_val_cmds()

    cmds = (f'{export_cmd};'
            f'python manage.py check;'
            f'python manage.py migrate;'
            f'python manage.py loaddata opendp_apps/dataverses/fixtures/*.json'
            f' opendp_apps/dataset/fixtures/*.json;')
#            f'python manage.py loaddata opendp_apps/dataverses/fixtures/test_dataverses_01.json'
#            f' opendp_apps/dataverses/fixtures/test_manifest_params_04.json;')


    print("Run init_db")
    print(f'Commands: {cmds}')
    fab_local(cmds)


def get_test_db_vals():
    """Return test database values"""
    db_vals = dict(DB_HOST='localhost',
                   DB_NAME='opendp_app',
                   DB_USER='opendp_user',
                   DB_PASSWORD='opendp_test_data')
    return db_vals
    # docker exec -it postgres-opendp-ux /bin/bash
    # psql -h localhost -d opendp_app -U opendp_user
    # select * from user_dataverseuser;


def get_export_db_val_cmds():
    """Return command similar to:"""
    db_vals = get_test_db_vals()
    export_vars = ' '.join([f'{key}={val}'
                            for key, val in db_vals.items()])
    export_vars = f'export {export_vars}'
    return export_vars

@task
def run_postgres(context):
    """Run Postgres via Docker on a local machine"""
    path_to_db_files = join(FAB_BASE_DIR, 'test_setup', 'postgres_data')
    if not isdir(path_to_db_files):
        os.makedirs(path_to_db_files, exist_ok=True)
    path_to_db_files = abspath(path_to_db_files)

    db_vals = get_test_db_vals()

    cmd = ('docker run --rm --name postgres-opendp-ux'
           f' -e POSTGRES_DB={db_vals["DB_NAME"]}'
           f' -e POSTGRES_USER={db_vals["DB_USER"]}'
           f' -e POSTGRES_PASSWORD={db_vals["DB_PASSWORD"]}'
           f' -v {path_to_db_files}:/var/lib/postgresql/data'
           ' -p 5432:5432 postgres')

    print(f'run-postgres: {cmd}')
    fab_local(cmd)



@task
def run_dev(context):
    """Run the Django development server"""
    init_db(context)
    create_django_superuser(context)

    export_cmd = get_export_db_val_cmds()

    fab_local(f'{export_cmd}; python manage.py runserver')

@task
def run_npm(context):
    """Run the Django development server"""

    fab_local(f'cd ../client; npm run serve')


@task
def dc_init_db(context):
    """Docker compose: Initialize the django database (if needed)"""

    cmds = (f'docker-compose run opendp_server python server/manage.py check;'
            'docker-compose run opendp_server python server/manage.py migrate;')

    print("Docker Compose: Run init_db")
    fab_local(cmds)

def dc_create_superuser(context):
    """Dockder compose: create a test superuser"""
    cmd = 'docker-compose run opendp_server fab -r ./server/ create-django-superuser'

    print("Docker Compose: create superuser")
    fab_local(cmd)

#@task
#def dc_run_dev(context):
#    """Docker compose: Run the Django development server"""
#    init_db(context)
#
 #   fab_local('docker-compose run python manage.py runserver')


def create_user(username, last_name, first_name, **kwargs):
    """Create a user. kwargs include:
        - new_password: default, create random pw
        - is_staff: default True
        - is_active: default True
        - is_superuser: default False
        - email: default ''
        - group_names: default []"""
    print(f'\nCreating user: {username}')

    from django.conf import settings
    if not settings.DEBUG:
        sys.exit('Only do this when testing')

    for key, val in get_test_db_vals().items():
        fmt_key = key.replace('DB_', '')
        settings.DATABASES["default"][fmt_key] = val

    from django.contrib.auth import get_user_model
    User = get_user_model()

    if User.objects.filter(username=username).count() > 0:
        print('Username "%s" already exists' % username)
        return

    rand_pw = ''.join(random.choice(string.ascii_lowercase + string.digits)
                      for _ in range(7))

    new_password = kwargs.get('new_password', rand_pw)

    new_user = User(username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=kwargs.get('email', ''),
                    is_staff=kwargs.get('is_staff', True),
                    is_active=kwargs.get('is_active', True),
                    is_superuser=kwargs.get('is_superuser', False))
    new_user.set_password(new_password)
    new_user.save()

    print((f'User created: "{username}"'
           f'\nPassword: "{new_password}"'))

@task
def create_django_superuser(context):
    """(Test only) Create superuser with username: dev_admin. Password is printed to the console."""
    from django.conf import settings
    if not settings.DEBUG:
        sys.exit('Only do this when testing')

    create_user(username='dev_admin',
                first_name='Dev',
                last_name='Administrator',
                email='opendp_admin@some.edu',
                **dict(new_password='admin',
                       is_superuser=True))

# -----------------------------------
#   Redis and celery tasks
# -----------------------------------
@task
def redis_run(context):
    """Run the redis server via Docker"""
    from django.conf import settings
    #redis_cmd = 'redis-server /usr/local/etc/redis.conf'
    redis_cmd = 'docker run --rm --name dpcreator-redis -p 6379:6379 -d redis:6'
    fab_local(redis_cmd)
    #with settings(warn_only=True):
    #    result = fab_local(redis_cmd, capture=True)

    #    if result.failed:
    #        print('Redis may already be running...')


@task
def redis_clear(context):
    """Clear data from the *running* local redis server"""
    redis_cmd = 'redis-cli flushall'    #  /usr/local/etc/redis.conf'
    fab_local(redis_cmd)


@task
def redis_stop(context):
    """Clear data from the *running* local redis server"""
    redis_cmd = 'docker stop dpcreator-redis'
    fab_local(redis_cmd)
    return
    #redis_cmd = 'pkill -f redis'
    redis_cmd = 'docker stop dpcreator-redis'
    with settings(warn_only=True):
        result = fab_local(redis_cmd, capture=True)

        if result.failed:
            print('Nothing to stop')

@task
def redis_restart(context):
    """Stop redis (if it's running) and start it again"""
    redis_stop(context)
    redis_run(context)

@task
def db_vars(context):
    """Show the export command for the db variables"""
    init_db(context)
    create_django_superuser(context)

    export_cmd = get_export_db_val_cmds()

    print(export_cmd)

@task
def celery_run(context):
    """Clear redis and Start celery"""
    import random, string
    rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    redis_clear(context)

    export_cmd = get_export_db_val_cmds()
    celery_cmd = (f'{export_cmd}; '
                  f'celery -A opendp_project worker'
                  f' -l info -n worker_{rand_str}@%%h')

    fab_local(celery_cmd)


@task
def celery_run(context):
    """Clear redis and Start celery"""
    import random, string
    rand_str = ''.join(random.choices(string.ascii_letters + string.digits, k=6))

    redis_clear(context)

    export_cmd = get_export_db_val_cmds()
    celery_cmd = (f'{export_cmd}; '
                  f'celery -A opendp_project worker'
                  f' -l info -n worker_{rand_str}@%%h')

    fab_local(celery_cmd)
"""
export DB_HOST=localhost DB_NAME=opendp_app DB_USER=opendp_user DB_PASSWORD=opendp_test_data
"""