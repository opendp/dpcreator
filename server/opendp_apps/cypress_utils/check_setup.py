import os

from django.conf import settings
from opendp_apps.cypress_utils import static_vals


# Should be the same value as settings.ALLOW_CYPRESS_ENDPOINT
#  within the the file opendp_project/settings/cypress_tests.py
#
def are_cypress_settings_in_place():
    """Three checks to see if cypress settings are running"""

    # (1) Settings module must be named 'opendp_project.settings.cypress_tests'
    #
    settings_name = os.environ.get('DJANGO_SETTINGS_MODULE')
    allowed_settings_for_del = ['opendp_project.settings.azure_test_01',
                                'opendp_project.settings.cypress_settings']
    if settings_name not in allowed_settings_for_del:
        print('are_cypress_settings_in_place? No, settings_name does not match')
        return False

    # (2a) Does settings have the variable ALLOW_CYPRESS_ENDPOINT
    #
    if not hasattr(settings, 'ALLOW_CYPRESS_ENDPOINT'):
        print('are_cypress_settings_in_place? No, variable ALLOW_CYPRESS_ENDPOINT not found')
        return False

    # (3) settings.ALLOW_CYPRESS_ENDPOINT equals ALLOW_CYPRESS_ENDPOINT_VALUE
    if settings.ALLOW_CYPRESS_ENDPOINT != static_vals.ALLOW_CYPRESS_ENDPOINT_VALUE:
        print('are_cypress_settings_in_place? No, variable ALLOW_CYPRESS_ENDPOINT has wrong value')
        return False

    return True

