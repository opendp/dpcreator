from opendp_apps.dataset.models import DepositorSetupInfo
from opendp_apps.dataset.tests.dataset_test_base import DatasetTestBase
from opendp_apps.model_helpers.msg_util import msgt


class TestDepositorInfo(DatasetTestBase):
    """Test the retrieval of DatasetInfo objects"""

    def setUp(self) -> None:
        super().setUp()

    def test_10_successful_patch(self):
        """(10) Successful patch"""
        msgt(self.test_10_successful_patch.__doc__)

        ds_dict = self.upload_file_via_api()

        update_payload = {'name': 'blueberry scone',
                          'description': 'this is a test'}

        response = self.client.patch(self.API_DATASET_INFO + ds_dict['object_id'] + '/',
                                     data=update_payload,
                                     content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['object_id'], ds_dict['object_id'])
        self.assertEqual(response.json()['name'], update_payload['name'])
        self.assertEqual(response.json()['description'], update_payload['description'])
        self.assertEqual(response.json()['status'], DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED)

    def test_20_patch_restricted_field(self):
        """(20) Try to patch a field that isn't allowed"""
        msgt(self.test_20_patch_restricted_field.__doc__)

        ds_dict = self.upload_file_via_api()

        update_payload = {'depositor_setup_info': {'has_data': False},
                          'source': 'marmalade',
                          'source_file': 'marmalade.txt',
                          'description': 'Give me a Vegemite sandwich'}

        response = self.client.patch(self.API_DATASET_INFO + ds_dict['object_id'] + '/',
                                     data=update_payload,
                                     content_type="application/json")

        # should skip the restricted fields such as depositor_setup_info, source, and source_file
        self.assertEqual(response.status_code, 200)

        # Match the original, no update
        self.assertEqual(response.json()['object_id'], ds_dict['object_id'])
        self.assertEqual(response.json()['depositor_setup_info'], ds_dict['depositor_setup_info'])
        self.assertEqual(response.json()['source'], ds_dict['source'])

        # description is updated
        self.assertEqual(response.json()['description'], update_payload['description'])

    def test_30_get_dataset_info(self):
        """(30) get dataset info"""
        msgt(self.test_30_get_dataset_info.__doc__)

        ds_dict = self.upload_file_via_api()

        response = self.client.get(self.API_DATASET_INFO + ds_dict['object_id'] + '/')

        # should skip the restricted fields such as depositor_setup_info, source, and source_file
        print('response', response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['object_id'], ds_dict['object_id'])
        self.assertEqual(response.json()['creator_id'], str(self.user_obj.object_id))

    def test_40_get_dataset_info_list(self):
        """(40) get dataset info list"""
        msgt(self.test_40_get_dataset_info_list.__doc__)

        ds_dict = self.upload_file_via_api()
        ds_dict2 = self.upload_second_file_via_api()
        ds_info_object_ids = [ds_dict['object_id'], ds_dict2['object_id']]

        response = self.client.get(self.API_DATASET_INFO)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)
        self.assertTrue(response.json()['results'][0]['object_id'] in ds_info_object_ids)
        self.assertTrue(response.json()['results'][1]['object_id'] in ds_info_object_ids)
