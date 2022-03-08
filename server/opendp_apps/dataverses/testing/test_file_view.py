import requests_mock

from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status

from opendp_apps.dataset import static_vals as dstatic
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataverses.models import ManifestTestParams
from opendp_apps.dataverses.testing import schema_test_data
from opendp_apps.user.models import OpenDPUser, DataverseUser
from opendp_apps.model_helpers.msg_util import msgt


class DataverseFileViewTest(TestCase):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                'test_opendp_users_01.json']

    def setUp(self) -> None:

        self.test_opendp_user = DataverseUser.objects.get(object_id='6c4986b1-e90d-48a2-98d5-3a37da1fd331').user

        # Create a DataverseHandoff object using the ManifestTestParams
        #   in fixture file: "test_manifest_params_04.json"
        #
        self.test_manifest_params = ManifestTestParams.objects.get(object_id='4bcad631-ce7c-475e-a569-29e71ee0b2ee')
        handoff_req = self.test_manifest_params.make_test_handoff_object()
        self.assertTrue(handoff_req.success is True)
        self.handoff_obj = handoff_req.data  # DataverseHandoff

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')
        self.client.force_login(self.user_obj)


    def test_05_manifest_params_url(self):
        """(05) manifest params url"""
        msgt(self.test_05_manifest_params_url.__doc__)

        # Test url reversal for dv-handoff
        test_url = self.test_manifest_params.dataverse_handoff_test_link()
        self.assertTrue('dv-handoff/dv_orig_create' in test_url)

        url_params = self.test_manifest_params.get_manifest_url_params()
        self.assertTrue(url_params in test_url)

    @requests_mock.Mocker()
    def test_10_successful_get(self, req_mocker):
        """(10) test_10_successful_get"""
        msgt(self.test_10_successful_get.__doc__)

        # The Mock url is for when the applications calls "Dataverse" to retrieve JSON-LD metadata
        #
        mock_url = ('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export'
                    '?exporter=schema.org&persistentId=doi:10.7910/DVN/PUXVDH'
                    '&User-Agent=pydataverse&key=shoefly-dont-bother-m3')
        req_mocker.get(mock_url, json=self.test_manifest_params.schema_org_content)

        response = self.client.get('/api/dv-file/',
                                   data={'handoff_id': self.handoff_obj.object_id,
                                         'creator': self.test_opendp_user.object_id},
                                   content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('success'), True)
        self.assertEqual(response.json().get('data'), [])

    @requests_mock.Mocker()
    def test_12_successful_creation(self, req_mocker):
        """(12) Successful file creation"""
        msgt(self.test_12_successful_creation.__doc__)

        # The Mock url is for when the applications calls "Dataverse" to retrieve JSON-LD metadata
        #
        mock_url = ('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export'
                    '?exporter=schema.org&persistentId=doi:10.7910/DVN/PUXVDH'
                    '&User-Agent=pydataverse&key=shoefly-dont-bother-m3')

        schema_content = self.test_manifest_params.schema_org_content
        req_mocker.get(mock_url, json=schema_content)

        response = self.client.post('/api/dv-file/',
                                    data={'handoff_id': self.handoff_obj.object_id,
                                          'creator': self.test_opendp_user.object_id},
                                    content_type='application/json')
        # print(response.json())
        # print('response.status_code', response.status_code)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get('success'), True)

        # 'message' should only appear when there's an error and we are displaying the error message
        self.assertTrue('message' not in response.json())

    @requests_mock.Mocker()
    def test_15_unsuccessful_creation(self, req_mocker):
        """(15) Schema.org retrieved but file specific info is not found!"""
        msgt(self.test_15_unsuccessful_creation.__doc__)

        # The Mock url is for when the applications calls "Dataverse" to retrieve JSON-LD metadata
        #
        mock_url = ('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export'
                    '?exporter=schema.org&persistentId=doi:10.7910/DVN/PUXVDH'
                    '&User-Agent=pydataverse&key=shoefly-dont-bother-m3')

        # Changing the schema org response so that it doesn't contain any file info
        schema_content = self.test_manifest_params.schema_org_content
        schema_content['distribution'] = []  # no file info

        req_mocker.get(mock_url, json=schema_content)

        response = self.client.post('/api/dv-file/',
                                    data={'handoff_id': self.handoff_obj.object_id,
                                          'creator': self.test_opendp_user.object_id},
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json().get('success'), False)
        self.assertTrue('message' in response.json())


    def test_20_schema_info_parsing(self):
        """(20) Retrieve the correct dataset from schema info, using File Ids"""
        msgt(self.test_20_schema_info_parsing.__doc__)

        # Schema contains file info, when file Id is an int
        #
        file_resp = DataverseManifestParams.get_file_specific_schema_info(
                            schema_test_data.schema_info_01,
                            file_id=schema_test_data.schema_info_01_file_id,
                            file_persistent_id=schema_test_data.schema_info_01_file_pid)

        self.assertTrue(file_resp.success is True)
        self.assertTrue('contentUrl' in file_resp.data)

        self.assertTrue(file_resp.data['contentUrl'].endswith(str(schema_test_data.schema_info_01_file_id)))

        # Schema contains file info, when file Id is a string
        #
        file_resp = DataverseManifestParams.get_file_specific_schema_info(
                                            schema_test_data.schema_info_01,
                                            file_id=str(schema_test_data.schema_info_01_file_id),
                                            file_persistent_id=schema_test_data.schema_info_01_file_pid)

        self.assertTrue(file_resp.success is True)
        self.assertTrue('contentUrl' in file_resp.data)
        self.assertTrue(file_resp.data['contentUrl'].endswith(str(schema_test_data.schema_info_01_file_id)))

    def test_30_schema_info_parsing_bad_id(self):
        """(30) Bad File Id used to retrieve data from schema info"""
        msgt(self.test_30_schema_info_parsing_bad_id.__doc__)

        # Bad File Id, as a string, used to retrieve data from schema info
        bad_file_id = '63'

        file_resp = DataverseManifestParams.get_file_specific_schema_info(
                            schema_test_data.schema_info_01,
                            file_id=bad_file_id,
                            file_persistent_id=schema_test_data.schema_info_01_file_pid)
        self.assertTrue(file_resp.success is False)
        self.assertTrue(file_resp.message.find(bad_file_id) > -1)

        # Schema does NOT contain file info, bad id as int
        #
        bad_file_id = 99999
        file_resp = DataverseManifestParams.get_file_specific_schema_info(
                            schema_test_data.schema_info_01,
                            file_id=bad_file_id,
                            file_persistent_id=schema_test_data.schema_info_01_file_pid)
        self.assertTrue(file_resp.success is False)
        self.assertTrue(file_resp.message.find(str(bad_file_id)) > -1)

    def test_40_schema_info_parsing(self):
        """(40) Retrieve the correct dataset from schema info, uses DOIs"""
        msgt(self.test_40_schema_info_parsing.__doc__)

        # Schema contains file info, when file Id is an int
        #
        file_resp = DataverseManifestParams.get_file_specific_schema_info(
            schema_test_data.schema_info_02,
            file_id=schema_test_data.schema_info_02_file_id,
            file_persistent_id=schema_test_data.schema_info_02_file_pid)

        self.assertTrue(file_resp.success is True)
        self.assertTrue('contentUrl' in file_resp.data)
        self.assertTrue(file_resp.data['identifier'].endswith(schema_test_data.schema_info_02_file_pid))

    @requests_mock.Mocker()
    def test_50_file_lock_message(self, req_mocker):
        """(50) Test dataset lock. Create a file and then try the same call with a different user"""
        msgt(self.test_50_file_lock_message.__doc__)

        # The Mock url is for when the applications calls "Dataverse" to retrieve JSON-LD metadata
        #
        mock_url = ('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export'
                    '?exporter=schema.org&persistentId=doi:10.7910/DVN/PUXVDH'
                    '&User-Agent=pydataverse&key=shoefly-dont-bother-m3')

        schema_content = self.test_manifest_params.schema_org_content
        req_mocker.get(mock_url, json=schema_content)

        # Create a DataverseFileInfo object
        #
        response = self.client.post('/api/dv-file/',
                                    data={'handoff_id': self.handoff_obj.object_id,
                                          'creator': self.test_opendp_user.object_id},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


        # Attempt to create the same DataverseFileInfo object with a different user
        #   - Should receive a file locked message
        #
        handoff_req = self.test_manifest_params.make_test_handoff_object()
        self.assertTrue(handoff_req.success is True)
        new_handoff_obj = handoff_req.data  # DataverseHandoff

        another_user = get_user_model().objects.get(username='dv_depositor')
        bad_response = self.client.post('/api/dv-file/',
                                        data={'handoff_id': new_handoff_obj.object_id,
                                              'creator': another_user.object_id},
                                        content_type='application/json')

        self.assertEqual(bad_response.status_code, status.HTTP_423_LOCKED)
        self.assertEqual(bad_response.json()['message'], dstatic.ERR_MSG_DATASET_LOCKED_BY_ANOTHER_USER)

    @requests_mock.Mocker()
    def test_60_handoff_id_removed_from_user(self, req_mocker):
        """(60) On unsuccessful file creation, if there's an OpenDPUser.handoff_id, it is removed"""
        msgt(self.test_60_handoff_id_removed_from_user.__doc__)

        # The Mock url is for when the applications calls "Dataverse" to retrieve JSON-LD metadata
        #
        mock_url = ('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export'
                    '?exporter=schema.org&persistentId=doi:10.7910/DVN/PUXVDH'
                    '&User-Agent=pydataverse&key=shoefly-dont-bother-m3')

        schema_content = self.test_manifest_params.schema_org_content
        req_mocker.get(mock_url, json=schema_content)

        # Add a handoff_id to the OpenDPUser object
        self.test_opendp_user.handoff_id = self.handoff_obj.object_id
        self.test_opendp_user.save()

        # Create a DataverseFileInfo object
        #
        response = self.client.post('/api/dv-file/',
                                    data={'handoff_id': self.handoff_obj.object_id,
                                          'creator': self.test_opendp_user.object_id},
                                    content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        retrieve_user = OpenDPUser.objects.get(object_id=self.test_opendp_user.object_id)
        self.assertTrue(retrieve_user.handoff_id is None)

    @requests_mock.Mocker()
    def test_70_handoff_id_stays_on_unsuccessful_creation(self, req_mocker):
        """(70) On unsuccessful file creation, if there's an OpenDPUser.handoff_id, it remains"""
        msgt(self.test_70_handoff_id_stays_on_unsuccessful_creation.__doc__)

        # The Mock url is for when the applications calls "Dataverse" to retrieve JSON-LD metadata
        #
        mock_url = ('http://127.0.0.1:8000/dv-mock-api/api/v1/datasets/export'
                    '?exporter=schema.org&persistentId=doi:10.7910/DVN/PUXVDH'
                    '&User-Agent=pydataverse&key=shoefly-dont-bother-m3')

        # Changing the schema org response so that it doesn't contain any file info
        schema_content = self.test_manifest_params.schema_org_content
        schema_content['distribution'] = []  # no file info

        req_mocker.get(mock_url, json=schema_content)

        # Add a handoff_id to the OpenDPUser object
        self.test_opendp_user.handoff_id = self.handoff_obj.object_id
        self.test_opendp_user.save()

        response = self.client.post('/api/dv-file/',
                                    data={'handoff_id': self.handoff_obj.object_id,
                                          'creator': self.test_opendp_user.object_id},
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test than the handoff_id is still there -- keeping there for now on failure
        #
        retrieve_user = OpenDPUser.objects.get(object_id=self.test_opendp_user.object_id)
        self.assertEqual(retrieve_user.handoff_id, self.handoff_obj.object_id)
