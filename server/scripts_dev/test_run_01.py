"""
Script to assist with loading tests data
"""
# Basic settings
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'opendp_project.settings.development_test'
from load_django_settings import *
load_local_settings()

# Additional imports
import json
import uuid
from http import HTTPStatus
from os.path import abspath, dirname, join
import requests
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.reverse import reverse as drf_reverse

from urllib.parse import urljoin
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataset.models import DepositorSetupInfo
from opendp_apps.dataset.serializers import DepositorSetupInfoSerializer
from opendp_apps.model_helpers.msg_util import msgt

API_HOST = 'http://localhost:8000'

class TestScenarioLoader:
    """Use for loading persistent data for testing"""

    def __init__(self):
        """Create an initial user and define file upload information"""
        username = 'dp_analyst1'
        user_pw = '123'
        self.auth_info = (username, user_pw)
        self.user_obj, _created = get_user_model().objects.get_or_create(username=username)
        self.user_obj.set_password(user_pw)
        self.user_obj.save()
        print('user object: ', self.user_obj)

        self.test_file_name = join(TEST_DATA_DIR,
                                   'teacher_survey',
                                   'teacher_survey.csv')
        self.upload_name = 'Teacher Survey'

        self.dataset_object_id = None

        self.run_test_setup()

    def run_test_setup(self):

        deposit_resp = self.upload_file_via_api()
        dataset_object_id = deposit_resp['object_id']

        dataset_info = self.get_dataset_info_via_api(dataset_object_id)
        print('dataset_info', dataset_info)

    def upload_file_via_api(self):
        """Convenience method to upload a file and return the response"""
        print('upload_file_via_api')

        payload = dict(name=self.upload_name,
                       creator=self.user_obj.object_id)

        files = {'source_file': open(self.test_file_name, 'rb')}

        upload_url = urljoin(API_HOST, '/api/direct-upload/')
        # print('reverse:', drf_reverse("direct-upload-create"))

        resp = requests.post(upload_url,
                             files=files,
                             data=payload,
                             auth=self.auth_info)

        assert resp.status_code == HTTPStatus.CREATED, "Expected 201 status code"

        jresp = resp.json()
        print('jresp\n', json.dumps(jresp, indent=4))
        return

        assert('object_id' in jresp), "Expected key 'object_id' in response"

        self.dataset_object_id = jresp['object_id']
        assert jresp['creator'] == str(self.user_obj.object_id), "Expected key 'creator' in response"
        assert jresp['name'] == self.upload_name, "Expected key 'name' in response"

        return jresp


    def get_dataset_info_via_api(self, dataset_object_id: str) -> dict:
        """Convenience method to get a dataset info object via the API"""
        assert dataset_object_id, "dataset_object_id cannot be None"

        dataset_info_url = urljoin(API_HOST, f'/api/dataset-info/{dataset_object_id}/')
        print('dataset_info_url', dataset_info_url)
        resp = requests.get(dataset_info_url, auth=self.auth_info)

        jresp = resp.json()
        print('jresp\n', json.dumps(jresp, indent=4))
        assert 'depositor_setup_info' in jresp, "Expected key 'depositor_setup_info' in response"
        assert 'object_id' in jresp['depositor_setup_info'], "Expected key 'object_id' in response"

        assert jresp['depositor_setup_info']['is_complete'] is False, \
            "Expected key 'is_complete' to be False in response"
        assert jresp['depositor_setup_info']['user_step'] == str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED),\
            f"Expected user step to be {str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED)}"

        return jresp

if __name__ == '__main__':
    tsl = TestScenarioLoader()