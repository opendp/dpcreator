import json
from os.path import abspath, dirname, join

from django.contrib.auth import get_user_model
from django.core.files import File as DjangoFileObject
from django.test import TestCase
from django.test import override_settings

from opendp_apps.analysis.analysis_plan_creator import AnalysisPlanCreator
from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.dataset.models import UploadFileInfo
from opendp_apps.utils import datetime_util

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')
FIXTURES_DIR = join(dirname(CURRENT_DIR), 'fixtures')


class StatSpecTestCase(TestCase):
    fixtures = ['test_analysis_002.json']  # ['test_dataset_data_001.json', ]

    API_ANALYSIS_PREFIX = '/api/analysis-plan/'
    API_RELEASE_PREFIX = '/api/release/'

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
        self.eye_typing_dataset.depositor_setup_info.is_complete = True
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
        analysis_plan = AnalysisPlan.objects.get(
            object_id=plan_creator.analysis_plan.object_id)

        self.assertEqual(plan_creator.analysis_plan.object_id, analysis_plan.object_id)

        return analysis_plan

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def get_release_info(self):
        """Convenience method to create a ReleaseInfo object"""
        analysis_plan = self.analysis_plan

        # The source_file should exist
        self.assertTrue(analysis_plan.dataset.source_file)

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = [self.general_stat_specs[2],
                                       self.general_stat_specs[1]]  # , self.general_stat_specs[2]]
        analysis_plan.save()

        params = dict(object_id=str(analysis_plan.object_id))

        response = self.client.post(self.API_RELEASE_PREFIX,
                                    json.dumps(params),
                                    content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertTrue('object_id' in response.json())

        new_release = ReleaseInfo.objects.get(object_id=response.json()['object_id'])
        self.assertEqual(new_release.get_analysis_plan_or_none().object_id,
                         analysis_plan.object_id)

        return new_release

    def test_for_available_epsilon(self):
        """Check for available epsilon"""
        plan = self.retrieve_new_plan()

        self.assertTrue(plan is not None)
        # self.assertEqual(2.0, AnalysisPlanCreator.get_available_epsilon(self.eye_typing_dataset))

        return
