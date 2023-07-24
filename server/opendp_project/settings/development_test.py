from opendp_project.settings.base import *

LOCAL_SETUP_DIR = os.path.join(BASE_DIR, 'test_setup')
USER_UPLOADED_DATA_DIR = os.path.join(LOCAL_SETUP_DIR, 'user_uploaded_data')
if not os.path.isdir(USER_UPLOADED_DATA_DIR):
    os.makedirs(USER_UPLOADED_DATA_DIR)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(LOCAL_SETUP_DIR, 'db_opendp_app.db3'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
    }
}

DEFAULT_LOGGER = 'console'

# DEV ONLY - For cypress management commands

# (1) This app includes the "clear_test_data" management command
INSTALLED_APPS += ['opendp_apps.cypress_utils']

# (2) This ROOT_URLCONF adds the API endpoint and view which uses the "clear_test_data" management command
#ROOT_URLCONF = 'opendp_project.urls_cypress'

# (3) ALLOW_CYPRESS_ENDPOINT value is set
#ALLOW_CYPRESS_ENDPOINT = 'cypress-in-ci-endpoint'

ALLOW_DEMO_LOADING = True