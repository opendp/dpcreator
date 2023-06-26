from unittest import skip

import requests_mock
from django.contrib.auth import get_user_model
from django.urls import reverse

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest
from opendp_apps.model_helpers.msg_util import msgt


@skip('Reconfiguring for analyst mode')
@requests_mock.Mocker()
class TestDataSetSerializer(BaseEndpointTest):
    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                'test_opendp_users_01.json',
                'test_dataset_data_001.json']

    def setUp(self) -> None:
        super(TestDataSetSerializer, self).setUp()
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')
        self.client.force_login(self.user_obj)

    def test_successful_get(self, req_mocker):
        """(10) Get inheritors of DataSetInfo"""
        msgt(self.test_successful_get.__doc__)
        self.set_mock_requests(req_mocker)
        response = self.client.get(reverse("datasetinfo-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 0, 'next': None, 'previous': None, 'results': []})

    def test_unsuccessful_get(self, req_mocker):
        """(15) Fail to get DataSetInfo"""
        msgt(self.test_unsuccessful_get.__doc__)
        self.set_mock_requests(req_mocker)
        self.client.logout()
        response = self.client.get(reverse("datasetinfo-list"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_successful_post(self, req_mocker):
        """(20) Create new inheritor of DataSetInfo"""
        msgt(self.test_successful_post.__doc__)
        self.set_mock_requests(req_mocker)
        response = self.client.post(reverse("datasetinfo-list"), {'resourcetype': 'DataverseFileInfo',
                                                                  'name': 'test',
                                                                  'creator': self.user_obj.username,
                                                                  'source': 'upload',
                                                                  'dataset_doi': 'test',
                                                                  'dataverse_file_id': 1,
                                                                  'installation_name': 'Harvard Dataverse'})
        response_json = response.json()

        # Examine this separately.
        # Since DepositorSetupInfo is created dynamically when the DataverseFileInfo is created, let's
        # remove fields that will have different values every time
        depositor_setup_info = response_json.pop('depositor_setup_info')
        depositor_setup_info.pop('object_id')
        depositor_setup_info.pop('created')
        depositor_setup_info.pop('updated')
        # depositor_setup_info.pop('creator')
        self.assertEqual(depositor_setup_info, {'id': 5,
                                                'dataset_questions': None,
                                                'epsilon_questions': None,
                                                'default_epsilon': None,
                                                'dataset_size': None,
                                                'epsilon': None,
                                                'default_delta': 0.0,
                                                'delta': 0.0,
                                                'confidence_level': astatic.CL_95,
                                                'is_complete': False,
                                                'user_step': 'step_100',
                                                'variable_info': None})

        # Tests against response with depositor info
        response_json.pop('object_id')
        response_json.pop('created')
        self.assertEqual(response_json, {'name': 'test',
                                         'creator': 'dv_depositor',
                                         'installation_name': 'Harvard Dataverse',
                                         'dataverse_file_id': 1,
                                         'dataset_doi': 'test',
                                         'file_doi': '',
                                         'status': 'step_100',
                                         'status_name': 'Step 1: Uploaded',
                                         'resourcetype': 'DataverseFileInfo',
                                         'dataset_schema_info': None,
                                         'file_schema_info': None,
                                         'analysis_plans': []})
        self.assertEqual(response.status_code, 201)

    def test_unsuccessful_post(self, req_mocker):
        """(25) Create new inheritor of DataSetInfo"""
        msgt(self.test_unsuccessful_post.__doc__)
        self.set_mock_requests(req_mocker)
        response = self.client.post(reverse("datasetinfo-list"), {'resourcetype': 'not a valid resourcetype',
                                                                  'name': 'test',
                                                                  'creator': self.user_obj.username,
                                                                  'source': 'not a valid source'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'resourcetype': 'Invalid resourcetype'})
