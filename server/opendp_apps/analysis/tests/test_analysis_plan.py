from os.path import abspath, dirname, isdir, isfile, join
import json
import responses

from unittest import skip
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder

from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.dataverse_download_handler import DataverseDownloadHandler
from opendp_apps.model_helpers.msg_util import msg, msgt
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.user.models import DataverseUser


CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(CURRENT_DIR), 'test_files')

class AnalysisPlanTest(TestCase):

    fixtures = ['test_profile_dataset_01.json',]

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

    @skip
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
