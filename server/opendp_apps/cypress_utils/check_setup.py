import os

from django.conf import settings
from opendp_apps.cypress_utils import static_vals


# Should be the same value as settings.ALLOW_CYPRESS_ENDPOINT
#  within the the file opendp_project/settings/cypress_tests.py
#
def are_cypress_settings_in_place():
    """Two checks to see if cypress settings are running"""

    # (1) Settings module must be named 'opendp_project.settings.cypress_tests'
    #
    settings_name = os.environ.get('DJANGO_SETTINGS_MODULE')
    if settings_name != 'opendp_project.settings.cypress_tests':
        return False

    # (2a) Settings has variable ALLOW_CYPRESS_ENDPOINT
    #
    if hasattr(settings, 'ALLOW_CYPRESS_ENDPOINT'):

        # (2b) settings.ALLOW_CYPRESS_ENDPOINT equals _ALLOW_CYPRESS_ENDPOINT_VAL
        if settings.ALLOW_CYPRESS_ENDPOINT == static_vals.ALLOW_CYPRESS_ENDPOINT_VAL:
            return True

    return False