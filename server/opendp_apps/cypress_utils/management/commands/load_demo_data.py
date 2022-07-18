"""
Allow deletion of data in between cypress tests
"""
import os
from os.path import abspath, dirname, isfile, join

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from allauth.account.models import EmailAddress as VerifyEmailAddress

from opendp_apps.analysis.models import AnalysisPlan, DepositorSetupInfo
from opendp_apps.cypress_utils import static_vals as cystatic
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

    def handle(self, *args, **options):
        """Delete data in-between user tests"""
        self.stdout.write(self.style.WARNING('>> Preparing to load demo data'))

        # Important check!!
        if not settings.ALLOW_DEMO_LOADING:  # Do not remove this check
            self.stdout.write(self.style.ERROR(cystatic.MESSAGE_CLEAR_DATA_CMD_ERR))
            return

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
                    data_profile=self.get_data_profile(),
                    profile_variables=self.get_data_profile(),
                    depositor_setup_info=depositor_setup,
                    )
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

        # Add AnalysisPlan
        #
        plan = AnalysisPlan(name=f'Plan {get_rand_alphanumeric(7)}',
                            analyst=analyst_user,
                            dataset=upload_file,
                            variable_info=depositor_setup.variable_info,
                            user_step=AnalysisPlan.AnalystSteps.STEP_0700_VARIABLES_CONFIRMED)

        plan.save()
        self.write_success_msg(f'AnalysisPlan created: {plan}')
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
            user_step=DepositorSetupInfo.DepositorSteps.STEP_0600_EPSILON_SET,
            dataset_questions=dataset_questions,
            epsilon_questions=epsilon_questions,
            variable_info=self.get_variable_info(),
            default_epsilon=1.0,
            epsilon=1.0,
            default_delta=1e-05,
            delta=1e-05,
            confidence_level=0.95
        )

        depositor_setup.save()

        return depositor_setup

    @staticmethod
    def get_data_profile() -> dict:
        """Return fixed data profile"""
        return {
               "dataset": {
                  "rowCount": 7000,
                  "variableCount": 10,
                  "variableOrder": [
                     [
                        0,
                        "sex"
                     ],
                     [
                        1,
                        "age"
                     ],
                     [
                        2,
                        "maritalstatus"
                     ],
                     [
                        3,
                        "Havingchild"
                     ],
                     [
                        4,
                        "highesteducationlevel"
                     ],
                     [
                        5,
                        "sourceofstress"
                     ],
                     [
                        6,
                        "smoking"
                     ],
                     [
                        7,
                        "optimisim"
                     ],
                     [
                        8,
                        "lifesattisfaction"
                     ],
                     [
                        9,
                        "selfesteem"
                     ]
                  ]
               },
               "variables": {
                  "age": {
                     "name": "age",
                     "type": "Integer",
                     "label": "",
                     "sort_order": 1
                  },
                  "sex": {
                     "name": "sex",
                     "type": "Integer",
                     "label": "",
                     "sort_order": 0
                  },
                  "smoking": {
                     "name": "smoking",
                     "type": "Categorical",
                     "label": "",
                     "categories": [

                     ],
                     "sort_order": 6
                  },
                  "optimisim": {
                     "name": "optimisim",
                     "type": "Categorical",
                     "label": "",
                     "categories": [

                     ],
                     "sort_order": 7
                  },
                  "selfesteem": {
                     "name": "selfesteem",
                     "type": "Categorical",
                     "label": "",
                     "categories": [

                     ],
                     "sort_order": 9
                  },
                  "Havingchild": {
                     "name": "Havingchild",
                     "type": "Categorical",
                     "label": "",
                     "categories": [

                     ],
                     "sort_order": 3
                  },
                  "maritalstatus": {
                     "name": "maritalstatus",
                     "type": "Integer",
                     "label": "",
                     "sort_order": 2
                  },
                  "sourceofstress": {
                     "name": "sourceofstress",
                     "type": "Categorical",
                     "label": "",
                     "categories": [

                     ],
                     "sort_order": 5
                  },
                  "lifesattisfaction": {
                     "name": "lifesattisfaction",
                     "type": "Categorical",
                     "label": "",
                     "categories": [

                     ],
                     "sort_order": 8
                  },
                  "highesteducationlevel": {
                     "name": "highesteducationlevel",
                     "type": "Integer",
                     "label": "",
                     "sort_order": 4
                  }
               }
            }

    @staticmethod
    def get_variable_info() -> dict:
        """Return fixed variable info"""
        return {
            "age": {
                "max": 75,
                "min": 20,
                "name": "age",
                "type": "Integer",
                "label": "age",
                "selected": True,
                "sortOrder": 1
            },
            "sex": {
                "max": 3,
                "min": 1,
                "name": "sex",
                "type": "Integer",
                "label": "sex",
                "selected": True,
                "sortOrder": 0
            },
            "smoking": {
                "max": 0,
                "min": 0,
                "name": "smoking",
                "type": "Categorical",
                "label": "smoking",
                "selected": True,
                "sortOrder": 6,
                "categories": [

                ]
            },
            "optimisim": {
                "max": 30,
                "min": 6,
                "name": "optimisim",
                "type": "Integer",
                "label": "optimisim",
                "selected": True,
                "sortOrder": 7,
                "categories": [

                ]
            },
            "selfesteem": {
                "max": 40,
                "min": 10,
                "name": "selfesteem",
                "type": "Integer",
                "label": "selfesteem",
                "selected": True,
                "sortOrder": 9,
                "categories": [

                ]
            },
            "havingchild": {
                "name": "Havingchild",
                "type": "Categorical",
                "label": "Havingchild",
                "selected": True,
                "sortOrder": 3,
                "categories": [

                ]
            },
            "maritalstatus": {
                "max": 8,
                "min": 1,
                "name": "maritalstatus",
                "type": "Integer",
                "label": "maritalstatus",
                "selected": True,
                "sortOrder": 2,
                "categories": [

                ]
            },
            "sourceofstress": {
                "max": 9,
                "min": 1,
                "name": "sourceofstress",
                "type": "Integer",
                "label": "sourceofstress",
                "selected": True,
                "sortOrder": 5,
                "categories": [

                ]
            },
            "lifesattisfaction": {
                "max": 35,
                "min": 5,
                "name": "lifesattisfaction",
                "type": "Integer",
                "label": "lifesattisfaction",
                "selected": True,
                "sortOrder": 8,
                "categories": [

                ]
            },
            "highesteducationlevel": {
                "max": 6,
                "min": 1,
                "name": "highesteducationlevel",
                "type": "Integer",
                "label": "highesteducationlevel",
                "selected": True,
                "sortOrder": 4
            }
        }
