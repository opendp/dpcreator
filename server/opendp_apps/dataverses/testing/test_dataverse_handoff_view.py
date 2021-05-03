from unittest import skip

import requests_mock

from django.test import TestCase
from django.contrib.auth import get_user_model

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import ManifestTestParams, DataverseHandoff
from opendp_apps.model_helpers.msg_util import msg, msgt


@requests_mock.Mocker()
class TestDataverseHandoffView(TestCase):
    """
    Should redirect to home in both cases, but with params
    in case of successful DataverseHandoff creation
    """

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json']

    def setUp(self):
        # test client
        self.client = APIClient()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        self.client.force_login(self.user_obj)

        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()

        self.data = {
            # 'dv_installation': 'https://dataverse.harvard.edu',
            'user': '4472310a-f591-403a-b8d6-dfb562f8b32f',
            'dv_handoff': '9e7e5506-dd1a-4979-a2c1-ec6e59e4769c',
            'persistent_id': 1,
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test',
            dv_static.DV_API_GENERAL_TOKEN: 1234,
            'dv_token_update': None,
            # TODO: Repeated field, camelcase is for parent model field, snakecase is for serializer
            dv_static.DV_PARAM_SITE_URL: 'https://dataverse.harvard.edu',
            dv_static.DV_PARAM_FILE_ID: 1,
            dv_static.DV_PARAM_DATASET_PID: 'doi:10.7910/DVN/B7DHBK'
        }

    def set_mock_requests(self, req_mocker):
        """
        Set up test urls that are used by the requests library
        """
        # Server Info
        server_info = {dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK,
                       'data': {'message': 'dataverse.MOCK-SERVER.edu'}}
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/info/server', json=server_info)

        # User Info
        user_info = {dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK, 'data': self.mock_params.user_info}
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/users/:me', json=user_info)

        # req_mocker.get('http://www.invalidsite.com/api/v1/users/:me')

        req_mocker.get('www.invalidsite.com/api/v1/users/:me')
        req_mocker.get('http://www.invalidsite.com/api/v1/users/:me')

        req_mocker.get('https://dataverse.harvard.edu/api/v1/users/:me')

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
        self.assertEqual(response.url, '/?error_code=site_url%2CfileId%2CdatasetPid%2CapiGeneralToken')

    def test_30_invalid_site_url_for_creation(self, req_mocker):
        """(30) test_invalid_site_url_for_creation"""
        msgt(self.test_30_invalid_site_url_for_creation.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-handoff-list')

        self.data[dv_static.DV_PARAM_SITE_URL] = 'https://invalidsite.com'
        response = self.client.post(url, data=self.data, format='json')
        msg(response)
        # Ensure redirect
        self.assertEqual(response.status_code, 302)
        # Other params are present and valid, so we should just see dv_installation here
        self.assertEqual(response.url, '/?error_code=site_url')
