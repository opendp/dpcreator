import json
from http import HTTPStatus
from os.path import abspath, dirname, join

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataset.models import DepositorSetupInfo

CURRENT_DIR = dirname(abspath(__file__))
FIXTURE_DATA_DIR = join(dirname(CURRENT_DIR), 'fixtures')
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class DatasetTestBase(TestCase):
    maxDiff = None
    API_DEPOSIT = '/api/depositor-setup-info/'
    API_DIRECT_UPLOAD = '/api/direct-upload/'
    API_DATASET_INFO = '/api/dataset-info/'

    def setUp(self):
        self.user_obj, _created = get_user_model().objects.get_or_create(username='rp')

        self.test_file_name = join('teacher_survey', 'teacher_survey.csv')
        self.upload_name = 'Teacher Survey'

        test_file = join(TEST_DATA_DIR, self.test_file_name)
        self.test_file_obj = SimpleUploadedFile(self.test_file_name,
                                                open(test_file, 'rb').read(),
                                                content_type="text/comma-separated-values")

        self.client.force_login(self.user_obj)

    def upload_file_via_api(self):
        """Convenience method to upload a file and return the response"""
        payload = dict(name=self.upload_name,
                       creator=self.user_obj.object_id,
                       source_file=self.test_file_obj)

        resp = self.client.post(self.API_DIRECT_UPLOAD,
                                data=payload)

        self.assertEqual(resp.status_code, HTTPStatus.CREATED)

        jresp = resp.json()

        self.assertEqual(jresp['creator_id'], str(self.user_obj.object_id))
        self.assertEqual(jresp['name'], self.upload_name)

        return jresp

    def upload_second_file_via_api(self):
        """Convenience method to upload a file and return the response"""

        # 2nd test file
        self.test_file_name2 = 'Fatigue_data.tab'
        self.upload_name2 = 'Teacher Survey'

        test_file2 = join(TEST_DATA_DIR, self.test_file_name2)
        self.test_file_obj2 = SimpleUploadedFile(self.test_file_name2,
                                                 open(test_file2, 'rb').read(),
                                                 content_type="text/tab-separated-values")

        payload = dict(name=self.upload_name2,
                       creator=self.user_obj.object_id,
                       source_file=self.test_file_obj2)

        resp = self.client.post(self.API_DIRECT_UPLOAD,
                                data=payload)

        self.assertEqual(resp.status_code, HTTPStatus.CREATED)

        jresp = resp.json()

        self.assertEqual(jresp['creator_id'], str(self.user_obj.object_id))
        self.assertEqual(jresp['name'], self.upload_name)

        return jresp

    def get_dataset_info_via_api(self, dataset_object_id: str) -> dict:
        """Convenience method to get a dataset info object via the API"""
        assert dataset_object_id, "dataset_object_id cannot be None"

        dataset_info_url = f'{self.API_DATASET_INFO}{dataset_object_id}/'
        resp = self.client.get(dataset_info_url)

        jresp = resp.json()
        self.assertTrue('depositor_setup_info' in jresp)
        self.assertTrue('object_id' in jresp['depositor_setup_info'])

        self.assertEqual(jresp['depositor_setup_info']['is_complete'], False)
        self.assertEqual(jresp['depositor_setup_info']['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED))

        return jresp

    def get_depositor_setup_info_via_api(self, dataset_object_id: str) -> DepositorSetupInfo:
        """Convenience method to get a depositor info object via the API"""
        assert dataset_object_id, "dataset_object_id cannot be None"

        setup_info_url = f'{self.API_DATASET_INFO}{dataset_object_id}/'
        resp = self.client.get(setup_info_url)

        jresp = resp.json()
        self.assertTrue('depositor_setup_info' in jresp)
        self.assertTrue('object_id' in jresp['depositor_setup_info'])

        return DepositorSetupInfo.objects.get(object_id=jresp['depositor_setup_info']['object_id'])

    def get_new_dataset_setup_info_id(self):
        """Create a new DatasetInfo object and return the **DepositorSetupInfo** object_id"""
        jresp = self.upload_file_via_api()

        return jresp['depositor_setup_info']['object_id']

    def populate_depositor_setup_info(self, depositor_setup_info: DepositorSetupInfo):
        """Fully populate the DepositorSetupInfo object except "is_complete" and "wizard_step" """
        assert depositor_setup_info, "depositor_setup_info cannot be None"

        new_variable_info = json.load(open(join(FIXTURE_DATA_DIR,
                                                'test_data_profile_teacher_survey.json'), 'r'))

        params = {'variable_info': new_variable_info,
                  'epsilon_questions': {"secret_sample": "no",
                                        "population_size": "not applicable",
                                        "observations_number_can_be_public": "no"},
                  'dataset_questions': {"radio_best_describes": "notHarmButConfidential",
                                        "radio_only_one_individual_per_row": "yes",
                                        "radio_depend_on_private_information": "yes"},
                  'default_epsilon': 1.0,
                  'default_delta': astatic.DELTA_10_NEG_5,
                  'epsilon': 0.5,
                  'delta': astatic.DELTA_10_NEG_5,
                  'confidence_level': astatic.CL_95
                  }

        # Update params
        for k, v in params.items():
            setattr(depositor_setup_info, k, v)
        depositor_setup_info.save()

        self.assertEqual(depositor_setup_info.is_complete, False)
        self.assertEqual(depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_0600_EPSILON_SET)

    def test_it(self):
        ds_info = self.upload_file_via_api()
        self.assertTrue('object_id' in ds_info)

        setup_info = self.get_depositor_setup_info_via_api(ds_info['object_id'])
        self.assertTrue(isinstance(setup_info, DepositorSetupInfo))
