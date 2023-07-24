"""
Allow deletion of data in between cypress tests
"""
import json
import os
from datetime import datetime, timedelta
from os.path import abspath, dirname, isfile, join

from allauth.account.models import EmailAddress as VerifyEmailAddress
from django.core.files import File
from django.core.management.base import BaseCommand

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.analysis_plan_creator import AnalysisPlanCreator
from opendp_apps.cypress_utils.management.commands.demo_loading_decorator import check_allow_demo_loading
from opendp_apps.dataset.models import DepositorSetupInfo
from opendp_apps.dataset.models import UploadFileInfo
from opendp_apps.user.models import OpenDPUser
from opendp_apps.utils.randname import get_rand_alphanumeric

DEMO_FILE_DIR = join(dirname(abspath(__file__)), 'demo_files')  # /cypress_utils/management/commands/demo_files

depositor_password = os.environ.get('USER_DEPOSITOR_PASSWORD', 'Test-for-2022')
analyst_password = os.environ.get('USER_ANALYST_PASSWORD', 'Test-for-2022')


class Command(BaseCommand):
    help = "Prepares data for demo / user testing"
    depositor_username = 'dp_depositor'
    analyst_username = 'dp_analyst'
    data_profile = None  # Placeholder to load dict from JSON file
    variable_info = None  # Placeholder to load dict from JSON file

    @check_allow_demo_loading  # Do not remove this check
    def handle(self, *args, **options):
        """Delete data in-between user tests"""
        self.stdout.write(self.style.WARNING('>> Preparing to load demo data'))

        if self.is_demo_data_already_loaded():
            return

        # Create users: depositor and analyst
        #
        depositor_user = OpenDPUser.objects.create(username=self.depositor_username,
                                                   first_name='DP',
                                                   last_name='Depositor',
                                                   email='test_depositor@opendp.org')
        depositor_user.set_password(depositor_password)
        depositor_user.save()
        self.write_success_msg(f'Depositor created: {depositor_user}')

        analyst_user = OpenDPUser.objects.create(username=self.analyst_username,
                                                 first_name='DP',
                                                 last_name='Analyst',
                                                 email='test_analyst@opendp.org')
        analyst_user.set_password(analyst_password)
        analyst_user.save()
        self.write_success_msg(f'Analyst created: {analyst_user}')

        # "Verify" users via email
        #
        verify_analyst = VerifyEmailAddress(user=analyst_user,
                                            email=analyst_user.email,
                                            primary=True,
                                            verified=True)
        verify_analyst.save()

        verify_depositor = VerifyEmailAddress(user=depositor_user,
                                              email=depositor_user.email,
                                              primary=True,
                                              verified=True)
        verify_depositor.save()

        # Create UploadFileInfo
        #
        depositor_setup = self.get_depositor_setup_info(analyst_user)
        self.write_success_msg(f'DepositorSetupInfo created: {depositor_setup}')

        upload_file = UploadFileInfo.objects.create(
            name='Teacher Survey',
            creator=analyst_user,
            depositor_setup_info=depositor_setup,
        )
        print('save upload file...')
        upload_file.save()

        self.write_success_msg(f'UploadFileInfo created: {upload_file}')

        # Add File to UploadFileInfo
        #
        filename = 'teacher_survey.csv'
        filepath = join(DEMO_FILE_DIR, filename)
        if not isfile(filepath):
            user_msg = f'Failed to find test data file: {filename}'
            self.stdout.write(self.style.ERROR(user_msg))
            return

        django_file = File(open(filepath, 'rb'))
        upload_file.source_file.save(filename, django_file)
        upload_file.save()
        self.write_success_msg(f'Data file attached to UploadFileInfo')

        # Depositor Setup Info re-saved to update step
        #
        depositor_setup.save()

        # Add AnalysisPlan
        #
        expiration_date = datetime.now() + timedelta(days=5)
        expiration_date_str = datetime.strftime(expiration_date, '%Y-%m-%d')
        plan_data = dict(object_id=str(upload_file.object_id),
                         name=f'Plan {get_rand_alphanumeric(7)}',
                         description='This is a test plan via the load_demo_data command',
                         epsilon=0.5,
                         expiration_date=expiration_date_str)

        plan_creator = AnalysisPlanCreator(analyst_user, plan_data)

        if plan_creator.has_error():
            print(plan_creator.get_err_msg())
            self.stdout.write(self.style.ERROR(plan_creator.get_err_msg()))
            return

        self.write_success_msg(f'AnalysisPlan created: {plan_creator.analysis_plan}')
        self.write_success_msg(f'>> Success! Process complete.', indent=False)

    def is_demo_data_already_loaded(self) -> bool:
        """Check if any of the demo data is already in the system"""
        if OpenDPUser.objects.filter(username=self.depositor_username).exists():
            user_msg = (f'The OpenDPUser "{self.depositor_username}" already exists.'
                        '\nPlease run "clear_test_data" before attempting to run the "load_demo_data" command')
            self.stdout.write(self.style.ERROR(user_msg))
            return True

        if OpenDPUser.objects.filter(username=self.analyst_username).exists():
            user_msg = (f'The OpenDPUser "{self.analyst_username}" already exists.'
                        '\nPlease run "clear_test_data" before attempting to run the "load_demo_data" command')
            self.stdout.write(self.style.ERROR(user_msg))
            return True

        return False

    def write_success_msg(self, user_msg: str, indent=True):
        """Print output statement"""
        if indent:
            user_msg = f'  - {user_msg}'
        self.stdout.write(self.style.SUCCESS(user_msg))

    def get_depositor_setup_info(self, analyst_user: OpenDPUser) -> DepositorSetupInfo:
        """Create and return a DepositorSetupInfo object"""

        dataset_questions = {"radio_best_describes": "notHarmButConfidential",
                             "radio_only_one_individual_per_row": "yes",
                             "radio_depend_on_private_information": "yes"}

        epsilon_questions = {"secret_sample": "no",
                             "population_size": "",
                             "observations_number_can_be_public": "yes"}

        depositor_setup = DepositorSetupInfo.objects.create(
            creator=analyst_user,
            dataset_questions=dataset_questions,
            epsilon_questions=epsilon_questions,
            variable_info=self.get_variable_info(),
            data_profile=self.get_data_profile(),
            default_epsilon=1.0,
            epsilon=1.0,
            default_delta=astatic.DELTA_10_NEG_5,
            delta=astatic.DELTA_10_NEG_5,
            confidence_level=astatic.CL_95,
        )

        depositor_setup.save()

        return depositor_setup

    def get_data_profile(self) -> dict:
        """Return fixed data profile from JSON file: teacher_survey_data_profile.json"""
        if not self.data_profile:
            self.data_profile = self.get_json_file_as_dict('teacher_survey_data_profile.json')

        return self.data_profile

    def get_variable_info(self) -> dict:
        """Return fixed variable_info from JSON file: teacher_survey_variable_info.json"""
        if not self.variable_info:
            self.variable_info = self.get_json_file_as_dict('teacher_survey_variable_info.json')

        return self.variable_info

    def get_json_file_as_dict(self, filename: str) -> dict:
        """Open a JSON file and return the contents as a Python dict"""
        filepath = join(DEMO_FILE_DIR, filename)
        if not isfile(filepath):
            user_msg = f'Failed to find test data file: {filepath}'
            self.stdout.write(self.style.ERROR(user_msg))
            return None

        json_content = open(filepath, 'r').read()

        file_dict = json.loads(json_content)

        self.write_success_msg(f'Loaded file to Python dict: {filename}')

        return file_dict
