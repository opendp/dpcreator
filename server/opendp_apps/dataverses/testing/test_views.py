import requests_mock

from rest_framework.reverse import reverse

from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest


@requests_mock.Mocker()
class TestDataverseUserView(BaseEndpointTest):
    """
    Placeholder for view-level tests
    """

    def test_successful_create(self, req_mocker):
        self.set_mock_requests(req_mocker)
        url = reverse('dv-user-list')
        response = self.client.post(url, data={'user': '42bb5733-97a3-411e-a60b-d35fadfb9689',
                                               'dv_handoff': '9e7e5506-dd1a-4979-a2c1-ec6e59e4769c'},
                                    format='json')
        self.assertNotEquals(response.status_code, None)

    def test_successful_update(self, req_mocker):
        self.set_mock_requests(req_mocker)
        url = reverse('dv-user-detail', kwargs={'pk': '4472310a-f591-403a-b8d6-dfb562f8b32f'})
        response = self.client.put(url,
                                   data=self.data,
                                   format='json')
        self.assertNotEquals(response.status_code, None)
