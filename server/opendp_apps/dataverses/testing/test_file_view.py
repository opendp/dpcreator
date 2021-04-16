import requests_mock

from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest
from opendp_apps.model_helpers.msg_util import msgt


@requests_mock.Mocker()
class FileViewGetTest(BaseEndpointTest):

    def test_10_successful_get(self, req_mocker):
        """(10) test_successful_creation"""
        msgt(self.test_10_successful_get.__doc__)

        self.set_mock_requests(req_mocker)

        response = self.client.get('/api/dv-file/',
                                   data={'handoff_id': '9e7e5506-dd1a-4979-a2c1-ec6e59e4769c',
                                         'user_id': '6c4986b1-e90d-48a2-98d5-3a37da1fd331'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.json().get('dataset_schema_info'))
        self.assertIsNotNone(response.json().get('file_schema_info'))
