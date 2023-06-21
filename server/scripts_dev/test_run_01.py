import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'opendp_project.settings.development_test'
from load_django_settings import *
load_local_settings()
print('okay')

import json
import uuid
from http import HTTPStatus
from os.path import abspath, dirname, join
import requests
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from urllib.parse import urljoin
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataset.models import DepositorSetupInfo
from opendp_apps.dataset.serializers import DepositorSetupInfoSerializer
from opendp_apps.model_helpers.msg_util import msgt

API_HOST = 'http://localhost:8000'

class TestScenarioLoader:
    """Use for loading persistent data for testing"""

    def __init__(self):
        """Load the data"""
        username = 'dp_analyst1'
        user_pw = '123'
        self.auth_info = (username, user_pw)
        self.user_obj, _created = get_user_model().objects.get_or_create(username=username)
        self.user_obj.set_password(user_pw)
        self.user_obj.save()

        self.test_file_name = join('teacher_survey', 'teacher_survey.csv')
        self.upload_name = 'Teacher Survey'

        test_file = join(TEST_DATA_DIR, self.test_file_name)
        self.test_file_obj = SimpleUploadedFile(self.test_file_name,
                                                open(test_file, 'rb').read(),
                                                content_type="text/comma-separated-values")

        self.upload_file_via_api()

    def upload_file_via_api(self):
        """Convenience method to upload a file and return the response"""
        payload = dict(name=self.upload_name,
                       creator=self.user_obj.object_id,
                       source_file=self.test_file_obj)

        upload_url = urljoin(API_HOST, '/api/direct-upload/')  # reverse("direct-upload-create")
        print('upload_url', upload_url)
        print('payload', payload)
        resp = requests.post(upload_url, data=payload, auth=self.auth_info)

        print('status code', resp.status_code)
        print('resp', resp.text)
        open('resp.html', 'w').write(resp.text)
        return
        self.assertEqual(resp.status_code, HTTPStatus.CREATED)

        jresp = resp.json()
        self.assertEqual(jresp['creator'], str(self.user_obj.object_id))
        self.assertEqual(jresp['name'], self.upload_name)

        return jresp


    def get_dataset_info_via_api(self, dataset_object_id: str) -> dict:
        """Convenience method to get a dataset info object via the API"""
        assert dataset_object_id, "dataset_object_id cannot be None"

        dataset_info_url = f'/api/dataset-info/{dataset_object_id}/'
        resp = self.client.get(dataset_info_url)

        jresp = resp.json()
        self.assertTrue('depositor_setup_info' in jresp)
        self.assertTrue('object_id' in jresp['depositor_setup_info'])

        self.assertEqual(jresp['depositor_setup_info']['is_complete'], False)
        self.assertEqual(jresp['depositor_setup_info']['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED))

        return jresp

if __name__ == '__main__':
    tsl = TestScenarioLoader()