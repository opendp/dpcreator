import json
from http import HTTPStatus
from os.path import abspath, dirname, join

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from opendp_apps.dataset.models import DepositorSetupInfo

CURRENT_DIR = dirname(abspath(__file__))
FIXTURE_DATA_DIR = join(dirname(CURRENT_DIR), 'fixtures')
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class DatasetTestBase(TestCase):
    maxDiff = None
    API_DEPOSIT = '/api/deposit/'
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

        print('jresp', json.dumps(jresp, indent=4))

        dataset_object_id = jresp['object_id']
        print(json.dumps(self.get_dataset_info_via_api(dataset_object_id),
                         indent=4))

    def test_it(self):
        self.get_new_dataset_setup_info_id()


