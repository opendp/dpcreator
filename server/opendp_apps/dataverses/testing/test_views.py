from unittest import skip

import requests_mock
from rest_framework.test import APIClient

from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest
from opendp_apps.model_helpers.msg_util import msgt


@requests_mock.Mocker()
class TestDataverseFileView(BaseEndpointTest):
    client = APIClient()
    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                'test_opendp_users_01.json']

    @skip('replacing with test_file_view.py')
    def test_10_list_successful(self, req_mocker):
        msgt(self.test_10_list_successful.__doc__)
        self.set_mock_requests(req_mocker)

        response = self.client.get('/api/dv-file/',
                                   data={'handoff_id': '9e7e5506-dd1a-4979-a2c1-ec6e59e4769c',
                                         'user_id': '6c4986b1-e90d-48a2-98d5-3a37da1fd331'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json().get('dv_installation'), 1)
