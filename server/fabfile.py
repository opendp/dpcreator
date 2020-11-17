"""Convenience commands"""
import os, sys
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
KEY_DEV_SETTINGS = 'opendp_project.settings'
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

    cmds = (f'python manage.py check;'
            'python manage.py migrate;'
            'python manage.py loaddata opendp_apps/dataverses/fixtures/test_dataverses_01.json'
            ' opendp_apps/dataverses/fixtures/test_manifest_params_03.json;')

    print("Run init_db")
    fab_local(cmds)

@task
def run_dev(context):
    """Run the Django development server"""
    init_db(context)
    create_django_superuser(context)
    fab_local('python manage.py runserver')

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

    create_user(username='admin',
                first_name='Dev',
                last_name='Administrator',
                email='opendp_admin@some.edu',
                **dict(new_password='admin',
                       is_superuser=True))
