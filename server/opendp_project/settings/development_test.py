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
