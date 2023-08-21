from opendp_project.settings.base import *

# ----------------------------------
# Azure specific settings
# ----------------------------------
# DEBUG = False
ASGI_APPLICATION = "opendp_project.asgi_azure.application"

# to test...
CORS_ALLOW_ALL_ORIGINS = True

#CORS_ALLOWED_ORIGINS = os.getenv('TRUSTED_ORIGINS', "TRUSTED_ORIGINS_ENV_VAR_MISSING").split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('TRUSTED_ORIGINS', "TRUSTED_ORIGINS_ENV_VAR_MISSING").split(',')

# Let nginx serve static files
USE_DEV_STATIC_SERVER = False

STATIC_ROOT = os.getenv('STATIC_ROOT', os.path.join(BASE_DIR, 'static_deploy', 'static', 'dist'))
if not os.path.isdir(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)

STATICFILES_DIRS = [
    # os.path.join(BASE_DIR, 'static')
    os.path.join(BASE_DIR, 'static', 'dist')
]

"""
Settings for running cypress tests
DANGER: This Cypress settings file introduces an API endpoint that deletes nearly all data.
 - This settings file makes that endpoint available accessible by doing the following:
 - This settings file makes that endpoint available accessible by doing the following:
 (1) Adding this Django app: 'opendp_apps.cypress_utils'
    - The app includes the "clear_test_data" management command
 (2) Using a different ROOT_URLCONF
    - This adds the API endpoint and view which uses the "clear_test_data" management command
 (3) The management command and extra url/endpoint are only run/added when the conditions in this
    function are met: opendp_app/cypress_utils/check_setup.py -> are_cypress_settings_in_place()
        -> Part of this check is that:
            settings.ALLOW_CYPRESS_TEST_ENDPOINT == cypress_utils.statics_vals.ALLOW_CYPRESS_TEST_ENDPOINT_VAL

"""
# (1) This app includes the "clear_test_data" management command
INSTALLED_APPS += ['opendp_apps.cypress_utils']

# (2) This ROOT_URLCONF adds the API endpoint and view which uses the "clear_test_data" management command
ROOT_URLCONF = 'opendp_project.urls_cypress'

# (3) ALLOW_CYPRESS_ENDPOINT value is set
ALLOW_CYPRESS_ENDPOINT = 'cypress-in-ci-endpoint'

ALLOW_DEMO_LOADING = True

DP_CREATOR_APP_NAME = os.environ.get('DP_CREATOR_APP_NAME', 'DP Creator (demo)')
