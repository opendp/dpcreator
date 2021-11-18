"""
Allow deletion of data in between cypress tests
"""
from django.apps import apps
from django.core.management.base import BaseCommand
from opendp_apps.cypress_utils.check_setup import are_cypress_settings_in_place
from opendp_apps.cypress_utils import static_vals as cystatic
from opendp_apps.user.models import OpenDPUser, DataverseUser

class Command(BaseCommand):
    help = "Deletes data for Cypress tests"

    def handle(self, *args, **options):
        """Delete data in-between Cypress tests"""

        # Important check!!
        if not are_cypress_settings_in_place(): # Do not remove this check
            self.stdout.write(self.style.ERROR(cystatic.MESSAGE_CLEAR_DATA_CMD_ERR))
            return

        models_to_clear = [('terms_of_access', ['TermsOfAccessLog']),
                           ('analysis', ['AnalysisPlan', 'ReleaseInfo', 'DepositorSetupInfo']),
                           ('dataset', ['UploadFileInfo', 'DataverseFileInfo', 'DataSetInfo']),
                           ('dataverses', ['DataverseHandoff']),
                           ('user', ['DataverseUser', 'OpenDPUser'])
                           ]

        self.stdout.write(self.style.WARNING('Preparing to delete test data'))

        for app_name, model_names in models_to_clear:
            for model_name in model_names:
                if model_name == 'OpenDPUser':
                    (del_cnt, _ignore) = OpenDPUser.objects \
                        .exclude(username__in=['test_user', 'dev_admin']).delete()
                    self.stdout.write(self.style.SUCCESS(f"{app_name}.{model_name} {del_cnt} instance(s) deleted."))
                elif model_name == 'DataverseUser':
                    (del_cnt, _ignore) = DataverseUser.objects \
                        .exclude(user__username__in=['test_user', 'dev_admin']).delete()
                    self.stdout.write(self.style.SUCCESS(f"{app_name}.{model_name} {del_cnt} instance(s) deleted."))
                else:
                    ye_model = apps.get_model(app_name, model_name)
                    (del_cnt, _ignore) = ye_model.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(f"{app_name}.{model_name} {del_cnt} instance(s) deleted."))

        self.stdout.write(self.style.SUCCESS(f">> Data deletion complete."))

