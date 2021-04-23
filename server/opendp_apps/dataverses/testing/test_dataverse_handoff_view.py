import requests_mock

from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest

from rest_framework.reverse import reverse
from opendp_apps.model_helpers.msg_util import msg, msgt


@requests_mock.Mocker()
class TestDataverseHandoffView(BaseEndpointTest):
    """
    Should redirect to home in both cases, but with params
    in case of successful DataverseHandoff creation
    """

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json']

    def test_10_successful_creation(self, req_mocker):
        """(10) test_successful_creation"""
        msgt(self.test_10_successful_creation.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-handoff-list')

        response = self.client.post(url, data=self.data, format='json')
        msg(response)
        # Ensure redirect
        self.assertEqual(response.status_code, 302)
        # Ensure there is only one param in the redirect URL, and that it is an id
        self.assertEqual(len(response.url.split('=')), 2)
        self.assertEqual(response.url.split('=')[0], '/?id')

    def test_20_blank_data_for_creation(self, req_mocker):
        """(20) test_blank_data_for_creation"""
        msgt(self.test_20_blank_data_for_creation.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-handoff-list')

        bad_data = {}
        response = self.client.post(url, data=bad_data, format='json')
        msg(response)
        # Ensure redirect
        self.assertEqual(response.status_code, 302)
        # Since no params passed, we expect them all to appear under error_code
        self.assertEqual(response.url, '/?error_code=site_url%2CfileId%2CdatasetPid')

    def test_30_invalid_site_url_for_creation(self, req_mocker):
        """(30) test_invalid_site_url_for_creation"""
        msgt(self.test_30_invalid_site_url_for_creation.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-handoff-list')

        self.data['site_url'] = 'https://invalidsite.com'
        response = self.client.post(url, data=self.data, format='json')
        msg(response)
        # Ensure redirect
        self.assertEqual(response.status_code, 302)
        # Other params are present and valid, so we should just see dv_installation here
        self.assertEqual(response.url, '/?error_code=site_url')
