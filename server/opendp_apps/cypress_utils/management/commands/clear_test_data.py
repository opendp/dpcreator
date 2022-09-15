"""
Allow deletion of data in between cypress tests
"""
from django.apps import apps
from django.core.management.base import BaseCommand

from opendp_apps.cypress_utils import static_vals as cystatic
from opendp_apps.cypress_utils.check_setup import are_cypress_settings_in_place
from opendp_apps.user.models import OpenDPUser, DataverseUser


class Command(BaseCommand):
    help = "Deletes data for Cypress tests"

    OPT_ARG_DATASETS_ONLY = 'datasets-only'
    OPT_VAL_DATASETS_ONLY = 'datasets_only'

    def add_arguments(self, parser):

        # Named (optional) arguments
        parser.add_argument(
            f'-ds-only',
            f'--{self.OPT_ARG_DATASETS_ONLY}',
            action='store_true',
            help=('Delete only the DatasetInfo and related objects including: '
                  'TermsOfAccessLog, DepositorSetupInfo, AnalysisPlan, and ReleaseInfo')
        )

    def handle(self, *args, **options):
        """Delete data in-between Cypress tests"""
        print('options: ', options)
        # Important check!!
        if not are_cypress_settings_in_place():  # Do not remove this check
            self.stdout.write(self.style.ERROR(cystatic.MESSAGE_CLEAR_DATA_CMD_ERR))
            return

        models_to_clear = [('terms_of_access', ['TermsOfAccessLog']),
                           ('analysis', ['AnalysisPlan', 'ReleaseInfo', 'DepositorSetupInfo']),
                           ('dataset', ['UploadFileInfo', 'DataverseFileInfo', 'DataSetInfo']),
                           ('dataverses', ['DataverseHandoff']),
                           # ('user', ['DataverseUser', 'OpenDPUser'])
                           ]
        user_models = ('user', ['DataverseUser', 'OpenDPUser'])

        self.stdout.write(self.style.WARNING('>> Preparing to delete test data'))

        if options[self.OPT_VAL_DATASETS_ONLY]:
            self.stdout.write(
                self.style.WARNING(f'   (Option: {self.OPT_ARG_DATASETS_ONLY})'))
        else:
            models_to_clear.append(user_models)

        for app_name, model_names in models_to_clear:
            for model_name in model_names:
                if model_name == 'OpenDPUser':
                    (del_cnt, _ignore) = OpenDPUser.objects \
                        .exclude(username__in=['test_user', 'dev_admin']).delete()
                    self.write_success_msg(f"{app_name}.{model_name} {del_cnt} instance(s) deleted.")
                elif model_name == 'DataverseUser':
                    (del_cnt, _ignore) = DataverseUser.objects \
                        .exclude(user__username__in=['test_user', 'dev_admin']).delete()
                    self.write_success_msg(f"{app_name}.{model_name} {del_cnt} instance(s) deleted.")
                else:
                    ye_model = apps.get_model(app_name, model_name)
                    (del_cnt, _ignore) = ye_model.objects.all().delete()
                    self.write_success_msg(f"{app_name}.{model_name} {del_cnt} instance(s) deleted.")

        self.write_success_msg(">> Data deletion complete.", indent=False)

    def write_success_msg(self, user_msg: str, indent=True):
        """Print output statement"""
        if indent:
            user_msg = f'  - {user_msg}'
        self.stdout.write(self.style.SUCCESS(user_msg))
