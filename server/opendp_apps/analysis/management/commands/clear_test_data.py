"""
Allow deletion of data in between cypress tests
"""
import os
import time

from django.apps import apps
from django.conf import settings
from django.core.management.base import BaseCommand

# Should be the same value as settings.ALLOW_CYPRESS_ENDPOINT
#  within the the file opendp_project/settings/cypress_tests.py
#
_ALLOW_CYPRESS_ENDPOINT_VAL = 'cypress-in-ci-endpoint'

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
        if settings.ALLOW_CYPRESS_ENDPOINT == _ALLOW_CYPRESS_ENDPOINT_VAL:
            return True

    return False

class Command(BaseCommand):
    help = "Deletes data for Cypress tests"

    def handle(self, *args, **options):
        """Delete data in-between Cypress tests"""
        if not are_cypress_settings_in_place():
            self.stdout.write(self.style.ERROR('This command is reserved for cypress testing'))
            return

        models_to_clear = [ ('terms_of_access', ['TermsOfAccessLog', 'TermsOfAccess']),
                            ('dataset', ['UploadFileInfo', 'DataverseFileInfo', 'DataSetInfo']),
                            ('analysis', ['ReleaseInfo', 'AnalysisPlan', 'DepositorSetupInfo']),
                            ('dataverses', ['ManifestTestParams', 'DataverseHandoff']),
                            ]
        self.stdout.write(self.style.WARNING('Preparing to delete test data'))

        for app_name, model_names in models_to_clear:
            for model_name in model_names:
                ye_model = apps.get_model(app_name, model_name)
                (del_cnt, _ignore) = ye_model.objects.all().delete()
                self.stdout.write(self.style.SUCCESS(f"{app_name}.{model_name} {del_cnt} instance(s) deleted."))

        self.stdout.write(self.style.SUCCESS(f">> Data deletion complete."))

