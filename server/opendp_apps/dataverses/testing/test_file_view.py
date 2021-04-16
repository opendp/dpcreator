from unittest import skip
import requests_mock

from django.test import TestCase

from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest
from opendp_apps.dataverses.testing import schema_test_data
from opendp_apps.model_helpers.msg_util import msgt


#@requests_mock.Mocker()
class FileViewGetTest(TestCase):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                'test_opendp_users_01.json']


    @skip('skipping')
    def test_10_successful_get(self, req_mocker):
        """(10) test_successful_creation"""
        msgt(self.test_10_successful_get.__doc__)

        self.set_mock_requests(req_mocker)

        response = self.client.get('/api/dv-file/',
                                   data={'handoff_id': '9e7e5506-dd1a-4979-a2c1-ec6e59e4769c',
                                         'user_id': '6c4986b1-e90d-48a2-98d5-3a37da1fd331'},
                                   content_type='application/json')
        self.assertEqual(response.status_code, 200)
        print(response.json())
        self.assertIsNotNone(response.json().get('dataset_schema_info'))
        self.assertIsNotNone(response.json().get('file_schema_info'))


    def test_20_schema_info_parsing(self):
        """Retrieve the correct dataset from schema info"""

        msgt('(20)(a) Schema contains file info, when file Id is an integer')
        file_resp = DataverseManifestParams.get_file_specific_schema_info(\
                                            schema_test_data.schema_info_01,
                                            file_id=schema_test_data.schema_info_01_file_id,
                                            file_persistent_id=schema_test_data.schema_info_01_file_pid)

        self.assertTrue(file_resp.success is True)
        self.assertTrue('contentUrl' in file_resp.data)
        self.assertTrue(file_resp.data['contentUrl'].endswith(str(schema_test_data.schema_info_01_file_id)))


        msgt('(20)(b) Schema contains file info, when file Id is a string')
        file_resp = DataverseManifestParams.get_file_specific_schema_info(\
                                            schema_test_data.schema_info_01,
                                            file_id=str(schema_test_data.schema_info_01_file_id),
                                            file_persistent_id=schema_test_data.schema_info_01_file_pid)

        self.assertTrue(file_resp.success is True)
        self.assertTrue('contentUrl' in file_resp.data)
        self.assertTrue(file_resp.data['contentUrl'].endswith(str(schema_test_data.schema_info_01_file_id)))

        msgt('(20)(c) Schema does NOT contain file info, bad id as string')
        bad_file_id = '63'
        file_resp = DataverseManifestParams.get_file_specific_schema_info(\
                                            schema_test_data.schema_info_01,
                                            file_id=bad_file_id,
                                            file_persistent_id=schema_test_data.schema_info_01_file_pid)
        self.assertTrue(file_resp.success is False)
        self.assertTrue(file_resp.message.find(bad_file_id) > -1)
        print(file_resp.message)

        msgt('(20)(d) Schema does NOT contain file info, bad id as int')
        bad_file_id = 99999
        file_resp = DataverseManifestParams.get_file_specific_schema_info(\
                                            schema_test_data.schema_info_01,
                                            file_id=bad_file_id,
                                            file_persistent_id=schema_test_data.schema_info_01_file_pid)
        self.assertTrue(file_resp.success is False)
        self.assertTrue(file_resp.message.find(str(bad_file_id)) > -1)
        print(file_resp.message)