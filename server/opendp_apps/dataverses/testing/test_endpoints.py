import json
import requests_mock

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import ManifestTestParams, DataverseHandoff
from opendp_apps.user.models import DataverseUser
from opendp_apps.model_helpers.msg_util import msg, msgt

TAG_WEB_CLIENT = 'web-client' # skip these tests on travis; need to fix as many use requests to access the localhost


class BaseEndpointTest(TestCase):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                'test_opendp_users_01.json']

    def setUp(self):

        # test client
        self.client = APIClient()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        # Object Ids used for most calls
        self.dp_user_object_id = self.user_obj.id
        self.dv_handoff_object_id = 1  # str(DataverseHandoff.objects.get(pk=1).object_id)

        self.non_existent_uuid = '29516628-488e-4f63-a9e0-4a660a22f54b' # I hope....

        self.client.force_login(self.user_obj)

        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()

        self.dv_updated_user_info = {'status': 'OK', 'data': {
                "id": 9974,
                "object_id": "2dd1aa0a-7e48-49e1-af0d-efbd2f68d0bf",
                "email": "mock_email_updated@some.edu",
                "firstName": "UpdatedFname",
                "lastName": "UpdatedLname",
                "superuser": False,
                "identifier": "@mock_user",
                "affiliation": "Some University",
                "createdTime": "2000-01-01T05:00:00Z",
                "displayName": "Mock User",
                "lastApiUseTime": "2020-11-16T19:34:51Z",
                "persistentUserId": "updatedPersistentUserId",
                "authenticationProviderId": "shib"
            }}
        self.dv_user_invalid_token = {
            "status": "ERROR",
            "message": "User with token 7957c20e-5316-47d5-bd23-2afd19f2d00a not found."
        }

        self.data = {
            # 'dv_installation': 'https://dataverse.harvard.edu',
            'user': '4472310a-f591-403a-b8d6-dfb562f8b32f',
            'dv_handoff': '9e7e5506-dd1a-4979-a2c1-ec6e59e4769c',
            'persistent_id': 1,
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test',
            'dv_general_token': 1234,
            'dv_sensitive_token': 1234,
            'dv_token_update': None,
            # TODO: Repeated field, camelcase is for parent model field, snakecase is for serializer
            dv_static.DV_PARAM_SITE_URL: 'https://dataverse.harvard.edu',
            'fileId': 1,
            'datasetPid': 'doi:10.7910/DVN/B7DHBK'
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

        req_mocker.get('www.invalidsite.com/api/v1/users/:me')
        req_mocker.get('http://www.invalidsite.com/api/v1/users/:me')

        req_mocker.get('https://dataverse.harvard.edu/api/v1/users/:me')

        dataset_info = {
            "@context": "http://schema.org",
            "@type": "Dataset",
            "@id": "https://doi.org/10.70122/FK2/AE07JZ",
            "identifier": "https://doi.org/10.70122/FK2/AE07JZ",
            "name": "GBS of CIMMYT bread wheat breeding lines from the year 2013-2020",
            "creator": [
                {
                    "name": "Alemie, Tilashwork", "affiliation": "Adet Agricultural Research Center, ARARI"}],
            "author": [{"name": "Alemie, Tilashwork", "affiliation": "Adet Agricultural Research Center, ARARI"}],
            "datePublished": "2021-03-31", "dateModified": "2021-03-31", "version": "1",
            "description": ["Bread wheat production improvement through crossing"],
            "keywords": ["Agricultural Sciences", "Bread wheat"],
            "citation": [{"@type": "CreativeWork", "text": "Tilashwork Alemie, 2021"}],
            "license": {"@type": "Dataset", "text": "CC0", "url": "https://creativecommons.org/publicdomain/zero/1.0/"},
            "includedInDataCatalog": {"@type": "DataCatalog", "name": "Demo Dataverse",
                                      "url": "https://demo.dataverse.org"},
            "publisher": {"@type": "Organization", "name": "Demo Dataverse"},
            "provider": {"@type": "Organization", "name": "Demo Dataverse"}
        }

        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export?exporter=schema.org&'
                       'persistentId=&User-Agent=pydataverse&key=some-token',
                       json=dataset_info)

        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export?exporter=schema.org&'
                       'persistentId=None&User-Agent=pydataverse',
                       json=dataset_info)

        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export?exporter='
                       'schema.org&persistentId=dataset_pid_etc&User-Agent=pydataverse&key=some-token',
                       json=dataset_info)

        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export?exporter=schema.org&'
                       'persistentId=&User-Agent=pydataverse&key=some-token',
                       json=dataset_info)

        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export?exporter=schema.org&'
                       'persistentId=None&User-Agent=pydataverse',
                       json={'distribution': 'just some mock data'})

    def get_basic_inputs(self, user_id, dataverse_handoff_id):
        """Return dict with key/vals for user_id and dataverse_handoff_id"""
        basic_params = {'user': user_id,
                        'dv_handoff': dataverse_handoff_id,
                        'dv_installation': 1,
                        'persistent_id': 1234}
        return basic_params


@requests_mock.Mocker()
class DataversePostTest(BaseEndpointTest):

    def test_10_successful_creation(self, req_mocker):
        """(10) test_successful_creation"""
        msgt(self.test_10_successful_creation.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-user-list')

        response = self.client.post(url, data=self.data, format='json')
        msg(response.json())
        self.assertEqual(response.status_code, 201)

    def test_20_user_not_found(self, req_mocker):
        """(20) test_user_not_found"""
        msgt(self.test_20_user_not_found.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-user-list')
        data = self.data
        data['user'] = '1234567a-f591-403a-b8d6-dfb562f8b32f'
        response = self.client.post(url, data=data, format='json')
        msg(f'server response: {response.json()}')
        self.assertEqual(response.status_code, 400)

    def test_30_dataverse_handoff_not_found(self, req_mocker):
        """(30) test_dataverse_handoff_not_found"""
        msgt(self.test_30_dataverse_handoff_not_found.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-user-list')

        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.site_url = 'www.invalidsite.com'
        dataverse_handoff.save()
        data = self.data
        data['dv_handoff'] = '1234567a-f591-403a-b8d6-dfb562f8b32f'

        response = self.client.post(url, data=data, format='json')
        msg(f'server response: {response.json()}')
        self.assertEqual(response.status_code, 400)

    def test_40_invalid_site_url(self, req_mocker):
        """(40) Test an invalid site url"""
        msgt(self.test_40_invalid_site_url.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.site_url = 'www.invalidsite.com'
        dataverse_handoff.save()
        print(f"All handoffs: {[x.__dict__ for x in DataverseHandoff.objects.all()]}")
        url = reverse('dv-user-list')

        response = self.client.post(url, data=self.data, format='json')
        msg(response.content)
        resp_json = response.json()
        print(resp_json)
        self.assertEqual(response.status_code, 400)
        self.assertTrue(resp_json['success'] is False)
        #self.assertTrue(resp_json['message'].find('www.invalidsite.com') > -1)
        self.assertTrue(resp_json['message'].find('failed to return a response') > -1)

    def test_50_invalid_token(self, req_mocker):
        """(50) Test an invalid token"""
        msgt(self.test_50_invalid_token.__doc__)

        # set the mock requests
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/users/:me',
                       json=self.dv_user_invalid_token)

        # Now test the API call which would be initiated from the Vue.js client
        #
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.apiGeneralToken = 'invalid_token_1234'
        dataverse_handoff.save()
        url = reverse('dv-user-list')

        response = self.client.post(url, data=self.data, format='json')

        msg(response.content)

        self.assertEqual(response.status_code, 400)

        resp_json = response.json()
        # self.assertTrue(resp_json['success'] is False)
        # self.assertTrue(resp_json['message'].find('Dataverse error') > -1)

    def test_60_duplicate_dataverse_user(self, req_mocker):
        msgt(self.test_60_duplicate_dataverse_user.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        url = reverse('dv-user-list')

        # Ensure there are no DataverseUsers
        DataverseUser.objects.all().delete()
        initial_dv_user_count = DataverseUser.objects.count()

        # Call once to create DataverseUser
        response = self.client.post(url, data=self.data, format='json')
        msg(response.json())
        self.assertEqual(response.status_code, 201)
        dataverse_users_count = DataverseUser.objects.count()
        self.assertEqual(initial_dv_user_count+1, dataverse_users_count)

        # Now make the same request, and demonstrate that it queried for DataverseUser
        # rather than creating another one
        response = self.client.post(url, data=self.data, format='json')
        msg(response.json())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(dataverse_users_count, DataverseUser.objects.count())


@requests_mock.Mocker()
class DataversePutTest(BaseEndpointTest):

    url = reverse('dv-user-detail', kwargs={'pk': '4472310a-f591-403a-b8d6-dfb562f8b32f'})

    def test_10_successful_update(self, req_mocker):
        """(10) test_successful_update"""
        msgt(self.test_10_successful_update.__doc__)

        # ---------------------------
        # set the mock request
        # contains updated name, email, and persistentId
        # ---------------------------
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/users/:me',
                       json=self.dv_updated_user_info)

        # ---------------------------
        # Update the user
        # ---------------------------
        orig_user = DataverseUser.objects.get(pk=2)
        #print('orig_user', orig_user, orig_user.id, orig_user.last_name, orig_user.first_name)

        response = self.client.put(self.url, data=self.data, format='json')

        msg(response.content)

        json_resp = response.json()
        self.assertTrue(json_resp['success'])

        self.assertEqual(response.status_code, 201)

        updated_user = DataverseUser.objects.get(pk=1)
        #print('updated_user', updated_user, updated_user.id, updated_user.last_name, updated_user.first_name)
        self.assertNotEqual(orig_user.first_name, updated_user.first_name)
        self.assertNotEqual(orig_user.last_name, updated_user.last_name)
        self.assertNotEqual(orig_user.email, updated_user.email)
        self.assertNotEqual(orig_user.persistent_id, updated_user.persistent_id)

    def test_20_user_not_found(self, req_mocker):
        """(20) test_user_not_found"""
        msgt(self.test_20_user_not_found.__doc__)

        self.set_mock_requests(req_mocker)

        data = self.data
        data['user'] = 0
        # Non-existent user object id
        url = reverse('dv-user-detail', kwargs={'pk': '1234567a-f591-403a-b8d6-dfb562f8b32f'})

        response = self.client.put(url, data=self.data, format='json')
        msg(response.content)

        self.assertEqual(response.status_code, 400)

    def test_30_dataverse_handoff_not_found(self, req_mocker):
        """(30) test_dataverse_handoff_not_found"""
        msgt(self.test_30_dataverse_handoff_not_found.__doc__)

        self.set_mock_requests(req_mocker)

        url = reverse('dv-user-detail', kwargs={'pk': '4472310a-f591-403a-b8d6-dfb562f8b32f'})

        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.site_url = 'www.invalidsite.com'
        dataverse_handoff.save()
        data = self.data
        # Non-existent handoff object id
        data['dv_handoff'] = '1234567a-f591-403a-b8d6-dfb562f8b32f'

        response = self.client.put(self.url, data=self.data, format='json')
        msg(response.content)

        self.assertEqual(response.status_code, 400)

    def test_40_invalid_site_url(self, req_mocker):
        """(40) test_invalid_site_url"""
        msgt(self.test_40_invalid_site_url.__doc__)

        self.set_mock_requests(req_mocker)

        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.site_url = 'www.invalidsite.com'
        dataverse_handoff.save()
        url = reverse('dv-user-detail', kwargs={'pk': '4472310a-f591-403a-b8d6-dfb562f8b32f'})

        response = self.client.put(self.url, data=self.data, format='json')
        msg(response.content)

        self.assertEqual(response.status_code, 400)

        response_json = json.loads(response.content)
        self.assertTrue(response_json['success'] is False)
        self.assertTrue(response_json['message'].find('failed to return a response') > -1)

    def test_50_invalid_token(self, req_mocker):
        """test_invalid_token"""
        msgt(self.test_50_invalid_token.__doc__)

        # set the mock requests
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/users/:me',
                       json=self.dv_user_invalid_token)

        # Now test the API call which would be initiated from the Vue.js client
        #
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.apiGeneralToken = 'invalid_token_1234'
        dataverse_handoff.save()
        url = reverse('dv-user-detail', kwargs={'pk': '4472310a-f591-403a-b8d6-dfb562f8b32f'})

        response = self.client.put(self.url, data=self.data, format='json')
        msg(response.content)

        self.assertEqual(response.status_code, 400)

        response_json = json.loads(response.content)
        self.assertTrue(response_json['success'] is False)
        self.assertTrue(response_json['message'].find('not found') > -1)
