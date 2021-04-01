import requests_mock

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse

from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest
from opendp_apps.dataverses.views import DataverseFileView
from opendp_apps.model_helpers.msg_util import msgt, msg


@requests_mock.Mocker()
class FileViewGetTest(BaseEndpointTest):

    def test_10_successful_get(self, req_mocker):
        """(10) test_successful_creation"""
        msgt(self.test_10_successful_get.__doc__)

        self.set_mock_requests(req_mocker)

        response = self.client.get('/api/dv-file/',
                                   data={'handoff_id': 'f7f5fab9-f51a-4aff-810b-374173132cd9',
                                         'user_id': '7121b28b-8a0f-4dc0-b46d-e23e43018010'},
                                   content_type='application/json')
        # print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get('dataset_schema_info'))
        self.assertIsNotNone(response.json().get('file_schema_info'))
