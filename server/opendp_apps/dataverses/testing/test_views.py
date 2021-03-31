import requests_mock

from rest_framework.test import APIClient

from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest


@requests_mock.Mocker()
class TestDataverseUserView(BaseEndpointTest):

    client = APIClient()

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                # This file needs a real token in order to run tests
                'test_dataverse_handoff_01.json',
                'test_opendp_users_01.json',
                'test_dataverse_user_01.json']

    def test_create(self, req_mocker):
        self.set_mock_requests(req_mocker)
        response = self.client.post('/api/dv-user/', data={'dv_installation': 1, 'user': 1, 'dv_handoff': 1})
        print(response.json())
        self.assertNotEquals(response, None)

    def test_update(self, req_mocker):
        self.set_mock_requests(req_mocker)
        response = self.client.put('/api/dv-user/1/', data={'dv_installation': 1, 'user': 1, 'dv_handoff': 1})
        self.assertNotEquals(response, None)
