import json
from os.path import abspath, dirname, isfile, join
from unittest import skip

import responses
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.test import TestCase
from rest_framework.test import APIClient

from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.dataverse_download_handler import DataverseDownloadHandler
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.user.models import DataverseUser

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(CURRENT_DIR), 'test_files')


class DownloadHandlerTests(TestCase):
    fixtures = ['test_profile_dataset_01.json', ]

    def setUp(self):

        # test client
        self.client = APIClient()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        # Object Ids used for most calls
        self.dp_user_object_id = self.user_obj.id

        self.client.force_login(self.user_obj)

        self.dv_user_invalid_token = {
            "status": "ERROR",
            "message": "User with token 7957c20e-5316-47d5-bd23-2afd19f2d00a not found."
        }

        self.dv_user_api_input_01 = {
            'user': '4472310a-f591-403a-b8d6-dfb562f8b32f',
            'dv_handoff': '9e7e5506-dd1a-4979-a2c1-ec6e59e4769c',
        }

    @responses.activate
    def test_10_download_profile_success(self):
        """(10) Test successful download + profile"""
        msgt(self.test_10_download_profile_success.__doc__)

        dfi = DataverseFileInfo.objects.get(pk=3)
        self.assertTrue(not dfi.source_file)

        crisis_filepath = join(TEST_DATA_DIR, 'crisis.tab')
        print('crisis_filepath', crisis_filepath)
        self.assertTrue(isfile(crisis_filepath))

        with open(crisis_filepath, "rb") as data_file:
            responses.add(
                responses.GET,
                "https://dataverse.harvard.edu/api/access/datafile/101649",
                body=data_file.read(),
                status=200,
                content_type="text/tab-separated-values",
                stream=True,
            )

        # ---------------------------
        # Run the Downloader!
        # ---------------------------
        dhandler = DataverseDownloadHandler(dfi)
        print('dhandler.has_error()', dhandler.has_error())
        self.assertTrue(dhandler.has_error() is False)

        print('dfi.source_file', dfi.source_file)
        self.assertTrue(dfi.source_file)

        print('>>> new_file_name', dhandler.new_file_name)
        self.assertEqual(dhandler.new_file_name, 'crisis.tab')

        # ---------------------------
        # Run the Profile Handler!
        # ---------------------------
        profile_handler = profiler_tasks.run_profile_by_filefield(dfi.object_id)
        print('profile_handler.has_error()', profile_handler.has_error())
        if profile_handler.has_error():
            print(profile_handler.get_err_msg())
        self.assertTrue(profile_handler.has_error() is False)

        # data profile exists
        self.assertTrue(profile_handler.data_profile)

        # check that the count of variables matches the actual number of variables
        profile = profile_handler.data_profile
        self.assertTrue(len(profile['variables']) == profile['dataset']['variableCount'])

        # check for several features within the profile
        json_profile = json.dumps(profile_handler.data_profile, cls=DjangoJSONEncoder, indent=4)
        for fn in ['WARCRI', 'WARCASE', 'SCMEDIAN']:
            self.assertTrue(json_profile.find(fn) > -1)

        # Check the status on depositor_setup_info.DepositorSetupInfo
        #
        dfi2 = DataverseFileInfo.objects.get(pk=3)
        self.assertEqual(dfi2.depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE)

    def test_20_error_no_file_schema(self):
        """(20) Error: No file_schema_info"""
        msgt(self.test_20_error_no_file_schema.__doc__)

        dfi = DataverseFileInfo.objects.get(pk=3)
        self.assertTrue(not dfi.source_file)

        # Set bad data, e.g. no file_schema_info
        #
        dfi.file_schema_info = ''

        # Run DataverseDownloadHandler
        #
        dhandler = DataverseDownloadHandler(dfi)

        # print('dhandler.has_error()', dhandler.has_error())
        self.assertTrue(dhandler.has_error())

        print(dhandler.get_err_msg())
        self.assertTrue(dhandler.get_err_msg().find('dv_download_020') > -1)

        # Check the status on depositor_setup_info.DepositorSetupInfo
        #
        dfi2 = DataverseFileInfo.objects.get(pk=3)
        # self.assertTrue(not dfi2.depositor_setup_info)
        self.assertEqual(dfi2.depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_9200_DATAVERSE_DOWNLOAD_FAILED)

    def test_30_error_no_content_url(self):
        """(30) Error: No "contentUrl" key in file_schema_info"""
        msgt(self.test_30_error_no_content_url.__doc__)

        dfi = DataverseFileInfo.objects.get(pk=3)
        self.assertTrue(not dfi.source_file)

        # set bad data
        bad_file_schema_info = dfi.file_schema_info
        bad_file_schema_info.pop(dv_static.SCHEMA_KEY_CONTENTURL)
        dfi.file_schema_info = bad_file_schema_info

        # Run DataverseDownloadHandler
        #
        dhandler = DataverseDownloadHandler(dfi)

        # print('dhandler.has_error()', dhandler.has_error())
        self.assertTrue(dhandler.has_error())

        print(dhandler.get_err_msg())
        self.assertTrue(dhandler.get_err_msg().find('dv_download_040') > -1)

        # Check the status on depositor_setup_info.DepositorSetupInfo
        #
        dfi2 = DataverseFileInfo.objects.get(pk=3)
        self.assertEqual(dfi2.depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_9200_DATAVERSE_DOWNLOAD_FAILED)

    def test_40_error_empty_content_url(self):
        """(40) Error: Empty "contentUrl" in file_schema_info"""
        msgt(self.test_40_error_empty_content_url.__doc__)

        dfi = DataverseFileInfo.objects.get(pk=3)
        self.assertTrue(not dfi.source_file)

        # set bad data
        bad_file_schema_info = dfi.file_schema_info
        bad_file_schema_info[dv_static.SCHEMA_KEY_CONTENTURL] = '    '
        dfi.file_schema_info = bad_file_schema_info

        # Run DataverseDownloadHandler
        #
        dhandler = DataverseDownloadHandler(dfi)
        # print('dhandler.has_error()', dhandler.has_error())
        self.assertTrue(dhandler.has_error())

        print(dhandler.get_err_msg())
        self.assertTrue(dhandler.get_err_msg().find('dv_download_050') > -1)

        # Check the status on depositor_setup_info.DepositorSetupInfo
        #
        dfi2 = DataverseFileInfo.objects.get(pk=3)
        self.assertEqual(dfi2.depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_9200_DATAVERSE_DOWNLOAD_FAILED)

    def test_50_no_dataverse_user(self):
        """(50) Error: No DataverseUser connected to the DataverseFileInfo.creator"""
        msgt(self.test_50_no_dataverse_user.__doc__)

        dfi = DataverseFileInfo.objects.get(pk=3)
        self.assertTrue(not dfi.source_file)

        # set bad data
        du = DataverseUser.objects.get(pk=3)
        du.delete()

        dhandler = DataverseDownloadHandler(dfi)
        # print('dhandler.has_error()', dhandler.has_error())
        self.assertTrue(dhandler.has_error())
        print(dhandler.get_err_msg())
        self.assertTrue(dhandler.get_err_msg().find('dv_download_070') > -1)

        # Check the status on depositor_setup_info.DepositorSetupInfo
        #
        dfi2 = DataverseFileInfo.objects.get(pk=3)
        self.assertEqual(dfi2.depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_9200_DATAVERSE_DOWNLOAD_FAILED)

    def test_60_no_dataverse_user_token(self):
        """(60) Error: DataverseUser doesn't have a token"""
        msgt(self.test_60_no_dataverse_user_token.__doc__)

        dfi = DataverseFileInfo.objects.get(pk=3)
        self.assertTrue(not dfi.source_file)

        # set bad data
        du = DataverseUser.objects.get(pk=3)
        du.dv_general_token = ''
        du.save()

        dhandler = DataverseDownloadHandler(dfi)
        # print('dhandler.has_error()', dhandler.has_error())
        self.assertTrue(dhandler.has_error())
        print(dhandler.get_err_msg())
        self.assertTrue(dhandler.get_err_msg().find('dv_download_080') > -1)

        # Check the status on depositor_setup_info.DepositorSetupInfo
        #
        dfi2 = DataverseFileInfo.objects.get(pk=3)
        self.assertEqual(dfi2.depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_9200_DATAVERSE_DOWNLOAD_FAILED)

    @responses.activate
    def test_70_download_no_schema_file_name(self):
        """(70) File Name not in schema, use download file name and add ".tab" """
        msgt(self.test_70_download_no_schema_file_name.__doc__)

        dfi = DataverseFileInfo.objects.get(pk=3)
        self.assertTrue(not dfi.source_file)

        # remove the "name" from the file_schema_info
        #
        updated_file_schema_info = dfi.file_schema_info
        updated_file_schema_info.pop(dv_static.SCHEMA_KEY_NAME)
        dfi.file_schema_info = updated_file_schema_info
        dfi.save()

        crisis_filepath = join(TEST_DATA_DIR, 'crisis.tab')
        print('crisis_filepath', crisis_filepath)
        self.assertTrue(isfile(crisis_filepath))

        with open(crisis_filepath, "rb") as data_file:
            responses.add(
                responses.GET,
                "https://dataverse.harvard.edu/api/access/datafile/101649",
                body=data_file.read(),
                status=200,
                content_type="text/tab-separated-values",
                stream=True,
            )

        # ---------------------------
        # Run the Downloader!
        # ---------------------------
        dhandler = DataverseDownloadHandler(dfi)
        # print('dhandler.has_error()', dhandler.has_error())
        self.assertTrue(not dhandler.has_error())

        print('dfi.source_file', dfi.source_file)
        self.assertTrue(dfi.source_file)

        print('>>> new_file_name', dhandler.new_file_name)
        self.assertEqual(dhandler.new_file_name, '101649.tab')

        # Check the status on depositor_setup_info.DepositorSetupInfo
        #
        dfi2 = DataverseFileInfo.objects.get(pk=3)
        self.assertEqual(dfi2.depositor_setup_info.user_step,
                         DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED)

    @skip
    @responses.activate
    def test_80_direct_profile(self):
        """(80) API endpoint: sucessfully run download and profile  """
        msgt(self.test_80_direct_profile.__doc__)

        dfi = DataverseFileInfo.objects.get(pk=3)
        self.assertTrue(not dfi.source_file)

        crisis_filepath = join(TEST_DATA_DIR, 'crisis.tab')
        print('crisis_filepath', crisis_filepath)
        self.assertTrue(isfile(crisis_filepath))

        with responses.RequestsMock() as rsps:
            with open(crisis_filepath, "rb") as data_file:
                rsps.add(
                    responses.GET,
                    "https://dataverse.harvard.edu/api/access/datafile/101649",
                    body=data_file.read(),
                    status=200,
                    content_type="text/tab-separated-values",
                    stream=True,
                )

                rsps.add(
                    responses.POST,
                    "http://dpcreator.org/api/profile/run-direct-profile/",
                    json.dumps({'success': True,
                                'data': {'dataset': {'variableCount': 19},
                                         'variables':
                                             {'SCMEDIAN':
                                                  {'type': pstatic.VAR_TYPE_NUMERICAL}
                                              }
                                         }
                                }),
                    status=200,
                    content_type='application/json',
                )
                # ---------------------------
                # Run the Profiler!
                # ---------------------------
                response = self.client.post('http://dpcreator.org/api/profile/run-direct-profile/',
                                            json.dumps({"object_id": "af0d01d4-073c-46fa-a2ff-829193828b82"}),
                                            content_type='application/json')

                print('response.content', response.content)
                self.assertEqual(response.status_code, 200)

                jresp = response.json()
                self.assertEqual(jresp.get('success'), True)
                self.assertEqual(jresp['data']['dataset']['variableCount'], 19)
                self.assertEqual(len(jresp['data']['variables']), 19)
                self.assertEqual(jresp['data']['variables']['SCMEDIAN']['type'], pstatic.VAR_TYPE_NUMERICAL)

    @skip
    @responses.activate
    def test_90_direct_profile_download_fail(self):
        """(90) API endpoint: fail to download file"""
        msgt(self.test_90_direct_profile_download_fail.__doc__)

        dfi = DataverseFileInfo.objects.get(pk=3)
        self.assertTrue(not dfi.source_file)

        with responses.RequestsMock() as rsps:
            rsps.add( \
                responses.GET,
                "https://dataverse.harvard.edu/api/access/datafile/101649",
                json={'error': 'not found'},
                status=404)

            # ---------------------------
            # Run the Profiler!
            # ---------------------------
            response = self.client.post('/api/profile/run-direct-profile/',
                                        json.dumps({"object_id": "af0d01d4-073c-46fa-a2ff-829193828b82"}),
                                        content_type='application/json')

            self.assertEqual(response.status_code, 200)
            jresp = response.json()
            # print(jresp)
            self.assertEqual(jresp.get('success'), False)
            self.assertTrue(jresp.get('message').find('failed') > -1)
