import json
from unittest import skip
import requests_mock

from django.test import Client, tag, TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import ManifestTestParams, DataverseHandoff, RegisteredDataverse
from opendp_apps.user.models import DataverseUser, OpenDPUser

TAG_WEB_CLIENT = 'web-client' # skip these tests on travis; need to fix as many use requests to access the localhost


class BaseEndpointTest(TestCase):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                # This file needs a real token in order to run tests
                'test_dataverse_handoff_01.json',
                'test_opendp_users_01.json',
                'test_dataverse_user_01.json']

    def setUp(self):

        # test client
        self.client = Client()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        self.client.force_login(self.user_obj)

        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()


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

        #req_mocker.get('http://www.invalidsite.com/api/v1/users/:me')

        # Schema.org dataset info
        schema_url = ('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export?exporter='
                      'schema.org&persistentId=doi:10.7910/DVN/PUXVDH')
        req_mocker.get(schema_url, json=self.mock_params.schema_org_content)

        # Schema.org dataset info - nonexistent dataset
        schema_url = ('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export?exporter='
                      'schema.org&persistentId=cool-breeze')
        fail_info = {dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_ERROR,
                     dv_static.DV_KEY_MESSAGE: 'not found for cool-breeze'}
        req_mocker.get(schema_url, json=fail_info)


@requests_mock.Mocker()
class DataversePostTest(BaseEndpointTest):

    def test_successful_creation(self, req_mocker):
        """Test a successful user creation call"""

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-user')
        response = self.client.post(url, data={'user_id': 1, 'dataverse_id': 1})
        self.assertEqual(response.status_code, 201)

    def test_user_not_found(self, req_mocker):
        """Test a non-existent OpenDP User id"""

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-user')
        response = self.client.post(url, data={'user_id': 0, 'dataverse_id': 1})
        self.assertEqual(response.status_code, 404)

    def test_dataverse_handoff_not_found(self, req_mocker):
        """Test a non-existent  DataverseHandoff id"""

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-user')
        response = self.client.post(url, data={'user_id': 1, 'dataverse_id': 0})
        self.assertEqual(response.status_code, 404)

    def test_invalid_site_url(self, req_mocker):
        """Test an invalid site url"""
        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.siteUrl = 'www.invalidsite.com'
        dataverse_handoff.save()
        url = reverse('dv-user')
        response = self.client.post(url, data={'user_id': 1, 'dataverse_id': 1})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['error'], 'Site www.invalidsite.com is not valid')


    def test_invalid_token(self, req_mocker):
        """Test an invalid token"""

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.apiGeneralToken = 'invalid_token_1234'
        dataverse_handoff.save()
        url = reverse('dv-user')
        response = self.client.post(url, data={'user_id': 1, 'dataverse_id': 0})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)['detail'], 'Not found.')


@requests_mock.Mocker()
class DataversePutTest(BaseEndpointTest):

    def test_successful_update(self, req_mocker):
        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        existing_dv_user = DataverseUser.objects.get(id=1)
        url = reverse('dv-user')
        response = self.client.put(url, data={'user_id': 1, 'dataverse_id': 1}, content_type='application/json')

        self.assertEqual(json.loads(response.content), {'dv_user': 1})
        self.assertEqual(response.status_code, 201)

        modified_dv_user = DataverseUser.objects.get(id=1)
        self.assertNotEqual(existing_dv_user.first_name, modified_dv_user.first_name)

    def test_user_not_found(self):
        url = reverse('dv-user')
        response = self.client.put(url, data={'user_id': 0, 'dataverse_id': 1}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_dataverse_handoff_not_found(self):
        url = reverse('dv-user')
        response = self.client.put(url, data={'user_id': 1, 'dataverse_id': 0}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_invalid_site_url(self):
        print('--- test_invalid_site_url ---')
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.siteUrl = 'www.invalidsite.com'
        dataverse_handoff.save()
        url = reverse('dv-user')
        response = self.client.put(url, data={"user_id": 1, "dataverse_id": 1}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['error'], 'Site www.invalidsite.com is not valid')

    def test_invalid_token(self):
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.apiGeneralToken = 'invalid_token_1234'
        dataverse_handoff.save()
        url = reverse('dv-user')
        response = self.client.put(url, data={'user_id': 1, 'dataverse_id': 0}, content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['detail'], 'Not found.')
