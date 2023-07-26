from http import HTTPStatus

from django.urls import reverse

from opendp_apps.dataset.models import DepositorSetupInfo
from opendp_apps.dataset.tests.dataset_test_base import DatasetTestBase
from opendp_apps.model_helpers.msg_util import msgt


class TestDepositorInfo(DatasetTestBase):
    """Test the retrieval of DatasetInfo objects"""

    def setUp(self) -> None:
        super().setUp()

    def test_010_successful_get(self):
        """(10) Get DatasetInfo list with no objects"""
        msgt(self.test_010_successful_get.__doc__)

        response = self.client.get(reverse("datasetinfo-list"))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {'count': 0, 'next': None, 'previous': None, 'results': []})

    def test_015_unsuccessful_get_not_logged_in(self):
        """(15) Fail to get DatasetInfo b/c not logged in"""
        msgt(self.test_015_unsuccessful_get_not_logged_in.__doc__)

        self.client.logout()
        response = self.client.get(reverse("datasetinfo-list"))
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_020_unallowed_post_bad_url(self):
        """(20) POST should be blocked on '/api/dataset-info/', creates are specific to the DatasetInfo subclasses, such as UploadFileInfo"""
        msgt(self.test_020_unallowed_post_bad_url.__doc__)

        payload = dict(name=self.upload_name,
                       creator=self.user_obj.object_id,
                       source_file=self.test_file_obj)

        print('reverse("datasetinfo-list")', reverse("datasetinfo-list"))
        resp = self.client.post(reverse("datasetinfo-list"),
                                data=payload)

        self.assertEqual(resp.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_030_successful_patch(self):
        """(30) Successful patch"""
        msgt(self.test_030_successful_patch.__doc__)

        ds_dict = self.upload_file_via_api()

        update_payload = {'name': 'blueberry scone',
                          'description': 'this is a test'}

        response = self.client.patch(self.API_DATASET_INFO + ds_dict['object_id'] + '/',
                                     data=update_payload,
                                     content_type="application/json")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['object_id'], ds_dict['object_id'])
        self.assertEqual(response.json()['name'], update_payload['name'])
        self.assertEqual(response.json()['description'], update_payload['description'])
        self.assertEqual(response.json()['status'], DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED)

    def test_040_patch_restricted_field(self):
        """(40) Try to patch a field that isn't allowed"""
        msgt(self.test_040_patch_restricted_field.__doc__)

        ds_dict = self.upload_file_via_api()

        update_payload = {'depositor_setup_info': {'has_data': False},
                          'source': 'marmalade',
                          'source_file': 'marmalade.txt',
                          'description': 'Give me a Vegemite sandwich'}

        response = self.client.patch(self.API_DATASET_INFO + ds_dict['object_id'] + '/',
                                     data=update_payload,
                                     content_type="application/json")

        # should skip the restricted fields such as depositor_setup_info, source, and source_file
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Match the original, no update
        self.assertEqual(response.json()['object_id'], ds_dict['object_id'])
        self.assertEqual(response.json()['depositor_setup_info'], ds_dict['depositor_setup_info'])
        self.assertEqual(response.json()['source'], ds_dict['source'])

        # description is updated
        self.assertEqual(response.json()['description'], update_payload['description'])

    def test_050_get_dataset_info(self):
        """(50) get dataset info"""
        msgt(self.test_050_get_dataset_info.__doc__)

        ds_dict = self.upload_file_via_api()

        response = self.client.get(self.API_DATASET_INFO + ds_dict['object_id'] + '/')

        # should skip the restricted fields such as depositor_setup_info, source, and source_file
        print('response', response.json())
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['object_id'], ds_dict['object_id'])
        self.assertEqual(response.json()['creator_id'], str(self.user_obj.object_id))

    def test_060_get_dataset_info_list(self):
        """(60) get dataset info list"""
        msgt(self.test_060_get_dataset_info_list.__doc__)

        ds_dict = self.upload_file_via_api()
        ds_dict2 = self.upload_second_file_via_api()
        ds_info_object_ids = [ds_dict['object_id'], ds_dict2['object_id']]

        response = self.client.get(self.API_DATASET_INFO)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['count'], 2)
        self.assertTrue(response.json()['results'][0]['object_id'] in ds_info_object_ids)
        self.assertTrue(response.json()['results'][1]['object_id'] in ds_info_object_ids)
