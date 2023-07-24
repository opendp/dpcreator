import json
from os.path import abspath, dirname, join

from django.contrib.auth import get_user_model
from django.core.files import File as DjangoFileObject
from django.test import TestCase

from opendp_apps.analysis.analysis_plan_creator import AnalysisPlanCreator
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.dataset.models import UploadFileInfo
from opendp_apps.utils import datetime_util

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')
FIXTURES_DIR = join(dirname(CURRENT_DIR), 'fixtures')


class StatSpecTestCase(TestCase):
    fixtures = ['test_analysis_002.json']  # ['test_dataset_data_001.json', ]

    def setUp(self):
        """Create an OpenDPUser, DatasetInfo, and AnalysisPlan"""
        user_params = dict(username='kpowers',
                           email='kpowers@ridiculous.edu',
                           first_name='Kenny',
                           last_name='Powers')
        self.user_obj, _created = get_user_model().objects.get_or_create(**user_params)

        # -------------------------------
        # Create eye-typing DatasetInfo + DepositorSetupInfo
        # -------------------------------
        params = {"name": "Replication Data for: Eye-typing experiment",
                  "creator": self.user_obj,
                  }
        self.eye_typing_dataset = UploadFileInfo(**params)

        fatigue_data_file_name = 'Fatigue_data.tab'
        test_file = join(TEST_DATA_DIR, fatigue_data_file_name)
        self.eye_typing_dataset.source_file.save(fatigue_data_file_name,
                                                 DjangoFileObject(open(test_file, 'rb')))

        self.eye_typing_dataset.depositor_setup_info.dataset_questions = {
            "radio_best_describes": "notHarmButConfidential",
            "radio_only_one_individual_per_row": "yes",
            "radio_depend_on_private_information": "yes"
        }
        self.eye_typing_dataset.depositor_setup_info.epsilon_questions = {
            "secret_sample": "no",
            "population_size": "",
            "observations_number_can_be_public": "yes"
        }

        eye_typing_variable_info = json.load(open(join(FIXTURES_DIR, 'eye_typing_variable_info.json')))

        self.eye_typing_dataset.depositor_setup_info.epsilon = 3.0
        self.eye_typing_dataset.depositor_setup_info.data_profile = eye_typing_variable_info['data_profile']
        self.eye_typing_dataset.depositor_setup_info.variable_info = eye_typing_variable_info['variable_info']
        self.eye_typing_dataset.depositor_setup_info.save()

        self.eye_typing_dataset.save()

    def retrieve_new_plan(self):
        """
        Convenience method to create a new AnalysisPlan
        """
        # Create a plan
        #
        plan_params = {"object_id": str(self.eye_typing_dataset.object_id),
                       "epsilon": 1.0,
                       "name": "Eye-typing Analysis Plan 1",
                       "description": "Analysis plan!",
                       "expiration_date": datetime_util.get_expiration_date_str()
                       }
        plan_creator = AnalysisPlanCreator(self.user_obj, plan_params)
        if plan_creator.has_error():
            print(plan_creator.get_error_message())
        self.assertTrue(plan_creator.has_error() is False)

        # Retrieve it
        analysis_plan = AnalysisPlan.objects.get(object_id=plan_creator.analysis_plan.object_id)

        self.assertEqual(plan_creator.analysis_plan.object_id, analysis_plan.object_id)

        return analysis_plan

    def test_for_available_epsilon(self):
        """Check for available epsilon"""
        plan = self.retrieve_new_plan()

        self.assertTrue(plan is not None)
        self.assertEqual(2.0, AnalysisPlanCreator.get_available_epsilon(self.eye_typing_dataset))

        return
        """
        from django.core.management import call_command

        object_to_serialize = ['user',
                               'dataset',
                               'analysis',
                               ]

        call_command('dumpdata',
                     object_to_serialize,
                     format='json',
                     indent=4)
        """