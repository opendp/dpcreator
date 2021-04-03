import json
import requests_mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest
from opendp_apps.model_helpers.msg_util import msgt


@requests_mock.Mocker()
class TestDataverseFileView(BaseEndpointTest):

    client = APIClient()
    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                # This file needs a real token in order to run tests
                'test_dataverse_handoff_01.json',
                'test_opendp_users_01.json',
                'test_dataverse_user_01.json']

    def test_10_list_successful(self, req_mocker):
        msgt(self.test_10_list_successful.__doc__)
        self.set_mock_requests(req_mocker)

        response = self.client.get('/api/dv-file/',
                                   data={'handoff_id': '9e7e5506-dd1a-4979-a2c1-ec6e59e4769c',
                                         'user_id': '6c4986b1-e90d-48a2-98d5-3a37da1fd331'})
        print(response.json())
        # print(response.content)
        self.assertEquals(response.status_code, 200)
        # Testing against ids can be tricky
        # self.assertEquals(response.json().get('id'), 4)
        self.assertEquals(response.json().get('dv_installation'), 1)

