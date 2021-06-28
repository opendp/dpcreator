import os
from opendp_project.settings.base import *

LOCAL_SETUP_DIR = os.path.join(BASE_DIR, 'test_setup', 'user_uploaded_data')
if not os.path.isdir(LOCAL_SETUP_DIR):
    os.makedirs(LOCAL_SETUP_DIR)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(LOCAL_SETUP_DIR, 'db_opendp_app.db3')
    }
}

