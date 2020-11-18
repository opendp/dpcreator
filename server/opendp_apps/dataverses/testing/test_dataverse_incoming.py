import json
from unittest import skip
import tempfile

from django.test import Client, tag, TestCase
from django.urls import reverse

from django.conf import settings
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import ManifestTestParams
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataverses.dataverse_request_handler import DataverseRequestHandler
from opendp_apps.user.models import DataverseUser
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.model_helpers.msg_util import msgt

TAG_WEB_CLIENT = 'web-client' # skip these tests on travis

class DataverseIncomingTest(TestCase):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json']

    def setUp(self):

        # test client
        self.client = Client()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        self.client.force_login(self.user_obj)

        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()


    def test_010_dv_params(self):
        """(10) Basic check of incoming DV params"""
        msgt(self.test_010_dv_params.__doc__)

        print('1. Retrieve mock params')
        #
        self.assertTrue(self.mock_params is not None)

        print('2. Area all params there? (should be yes)')
        #
        params_dict = self.mock_params.as_dict()
        dv_manifest = DataverseManifestParams(params_dict)
        #print(dv_manifest.get_error_message())
        self.assertTrue(dv_manifest.has_error() is False)

        print('3. Test with missing param. fileId')
        #
        params_dict.pop('fileId')
        dv_manifest = DataverseManifestParams(params_dict)
        self.assertTrue(dv_manifest.has_error())

        err_msg = dv_manifest.get_error_message()
        self.assertTrue(err_msg.find('required parameter is missing') > -1)
        self.assertTrue(err_msg.find('fileId') > -1)
        print(dv_manifest.get_error_message())

        print('4. Test with missing params. fileId, apiGeneralToken')
        #
        params_dict.pop('apiGeneralToken')
        dv_manifest = DataverseManifestParams(params_dict)
        self.assertTrue(dv_manifest.has_error())

        err_msg = dv_manifest.get_error_message()
        self.assertTrue(err_msg.find('required parameters are missing') > -1)
        self.assertTrue(err_msg.find('fileId') > -1)
        self.assertTrue(err_msg.find('apiGeneralToken') > -1)
        print(dv_manifest.get_error_message())


    def test_020_check_dv_handler_directly(self):
        """(20) Test DataverseRequestHandler directly"""
        msgt(self.test_020_check_dv_handler_directly.__doc__)

        print('1. Shouldn\'t be any existing DataverseUser objects')
        self.assertTrue(DataverseUser.objects.count() == 0)

        print('2. Process incoming request')
        dv_handler = DataverseRequestHandler(self.mock_params.as_dict(), self.user_obj)
        if dv_handler.has_error():
            print(dv_handler.get_err_msg())

        self.assertTrue(dv_handler.has_error() is False)

        print('3. Has a DataverseUser been created?')
        dv_user = DataverseUser.objects.filter(user=self.user_obj).first()
        self.assertTrue(dv_user is not None)
        self.assertEqual(dv_user.email, 'mock_user@some.edu')  # from test_manifest_params_04.json
        self.assertEqual(dv_user.first_name, 'Mock')  # from test_manifest_params_04.json
        self.assertEqual(dv_user.last_name, 'User')  # from test_manifest_params_04.json

        print('4. Has a DataverseUser file info object been created?')
        file_info = DataverseFileInfo.objects.filter(creator=self.user_obj, dataverse_file_id=self.mock_params.fileId).first()
        self.assertTrue(file_info is not None)
        #print('----' + f'{DataverseFileInfo.objects.count()}' + '----------')


    def test_030_dv_handler_bad_param(self):
        """(30) Test DataverseRequestHandler with bad params"""
        msgt(self.test_030_dv_handler_bad_param.__doc__)

        print('1. Test with bad file id param')
        params = self.mock_params.as_dict()
        params[dv_static.DV_PARAM_FILE_ID] = 777777  # bad file Id
        dv_handler = DataverseRequestHandler(params, self.user_obj)

        self.assertTrue(dv_handler.has_error())
        print(dv_handler.get_err_msg())
        self.assertTrue(dv_handler.get_err_msg().find(dv_static.DV_PARAM_FILE_ID) > -1)


        print('2. Test with bad datasetPid param')
        params = self.mock_params.as_dict()
        params[dv_static.DV_PARAM_DATASET_PID] = 'cool-breeze'  # datasetPid
        dv_handler = DataverseRequestHandler(params, self.user_obj)
        print('schema_info', dv_handler.schema_info)
        self.assertTrue(dv_handler.has_error())
        print(dv_handler.get_err_msg())
        self.assertTrue(dv_handler.get_err_msg().find('cool-breeze' ) > -1)
        self.assertTrue(dv_handler.schema_info is None)


    @tag(TAG_WEB_CLIENT)
    def test_100_check_dv_handler_via_url(self):
        """(100) Test DataverseRequestHandler via url"""
        msgt(self.test_100_check_dv_handler_via_url.__doc__)
        print('1. Go to page with valid params')

        url = reverse('view_dataverse_incoming_2') + '?' + self.mock_params.get_manifest_url_params()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Look for content on the web page
        page_content = response.content.decode()

        print('2. Find title text on web page')
        #
        self.assertTrue(page_content.find('Replication Data for: Eye-typing experiment') > -1)

        print('3. Find Dataverse user email on web page')
        #
        self.assertTrue(page_content.find('mock_user@some.edu') > -1)

        print('4. Has a DataverseUser been created?')
        dv_user = DataverseUser.objects.filter(user=self.user_obj).first()
        self.assertTrue(dv_user is not None)
        self.assertEqual(dv_user.email, 'mock_user@some.edu')  # from test_manifest_params_04.json
        self.assertEqual(dv_user.first_name, 'Mock')  # from test_manifest_params_04.json
        self.assertEqual(dv_user.last_name, 'User')  # from test_manifest_params_04.json

        print('5. Has a DataverseUser file info object been created?')
        file_info = DataverseFileInfo.objects.filter(creator=self.user_obj).first()
        self.assertTrue(file_info is not None)

    @tag(TAG_WEB_CLIENT)
    def test_110_check_dv_handler_via_url_no_params(self):
        """(110) Test DataverseRequestHandler via url with no parameters"""
        msgt(self.test_110_check_dv_handler_via_url_no_params.__doc__)

        print('1. Go to page with NO params')
        #
        url = reverse('view_dataverse_incoming_2')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        page_content = response.content.decode()
        print('2. Find error message on web page')
        #
        self.assertTrue(page_content.find('These required parameters are missing') > -1)