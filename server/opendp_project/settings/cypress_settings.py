"""
Settings for running cypress tests
DANGER: This Cypress settings file introduces an API endpoint that deletes nearly all data.
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
import os

from opendp_project.settings.base import *

DEBUG = True

# (1) This app includes the "clear_test_data" management command
INSTALLED_APPS += ['opendp_apps.cypress_utils']

# (2) This ROOT_URLCONF adds the API endpoint and view which uses the "clear_test_data" management command
ROOT_URLCONF = 'opendp_project.urls_cypress'

# (3) ALLOW_CYPRESS_ENDPOINT value is set
ALLOW_CYPRESS_ENDPOINT = 'cypress-in-ci-endpoint'


ACCOUNT_EMAIL_VERIFICATION = os.environ.get('ACCOUNT_EMAIL_VERIFICATION', 'none')  # 'mandatory'
print('ACCOUNT_EMAIL_VERIFICATION', ACCOUNT_EMAIL_VERIFICATION)