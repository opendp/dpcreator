from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase

from opendp_apps.model_helpers.msg_util import msgt


class TestDataSetSerializer(APITestCase):

    fixtures = ['test_dataset_data_001.json']

    def setUp(self) -> None:
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')
        self.client.force_login(self.user_obj)

    def test_successful_get(self):
        """(10) Get inheritors of DataSetInfo"""
        msgt(self.test_successful_get.__doc__)
        response = self.client.get(reverse("datasetinfo-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 0, 'next': None, 'previous': None, 'results': []})

    def test_unsuccessful_get(self):
        """(15) Fail to get DataSetInfo"""
        msgt(self.test_unsuccessful_get.__doc__)
        self.client.logout()
        response = self.client.get(reverse("datasetinfo-list"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_successful_post(self):
        """(20) Create new inheritor of DataSetInfo"""
        msgt(self.test_successful_post.__doc__)
        response = self.client.post(reverse("datasetinfo-list"), {'resourcetype': 'DataverseFileInfo',
                                                                  'name': 'test',
                                                                  'creator': self.user_obj.username,
                                                                  'source': 'upload',
                                                                  'dataset_doi': 'test',
                                                                  'dataverse_file_id': 1,
                                                                  'installation_name': 'Harvard Dataverse',
                                                                  'depositor_setup_info': 1})
        response_json = response.json()
        # Remove object_id, and created since they will be different every time the test is run
        # which makes equality testing difficult
        object_id = response_json.pop('object_id')
        created = response_json.pop('created')
        self.assertEqual(response_json, {'name': 'test',
                                         'creator': 'dv_depositor',
                                         'installation_name': 'Harvard Dataverse',
                                         'dataverse_file_id': 1,
                                         'dataset_doi': 'test',
                                         'file_doi': '',
                                         'status': 'step_100',
                                         'status_name': 'Step 1: Uploaded',
                                         'resourcetype': 'DataverseFileInfo'}
)
        self.assertEqual(response.status_code, 201)

    def test_unsuccessful_post(self):
        """(25) Create new inheritor of DataSetInfo"""
        msgt(self.test_unsuccessful_post.__doc__)
        response = self.client.post(reverse("datasetinfo-list"), {'resourcetype': 'not a valid resourcetype',
                                                                  'name': 'test',
                                                                  'creator': self.user_obj.username,
                                                                  'source': 'not a valid source'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'resourcetype': 'Invalid resourcetype'})
