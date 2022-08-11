from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import ManifestTestParams


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

        self.non_existent_uuid = '29516628-488e-4f63-a9e0-4a660a22f54b'  # I hope....

        self.client.force_login(self.user_obj)

        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()

        self.dv_user_url = reverse('dv-user-list')

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

        self.dv_user_api_input_01 = {
            'user': '4472310a-f591-403a-b8d6-dfb562f8b32f',
            'dv_handoff': '9e7e5506-dd1a-4979-a2c1-ec6e59e4769c',
        }

    def set_mock_requests(self, req_mocker):
        """
        Set up test urls that are used by the requests library
        """
        server_info = {
            dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK,
            'data': {'message': 'dataverse.MOCK-SERVER.edu'}
        }
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/info/server', json=server_info)

        # User Info
        user_info = {dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK, 'data': self.mock_params.user_info}
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/users/:me', json=user_info)

        # req_mocker.get('http://www.invalidsite.com/api/v1/users/:me')

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
