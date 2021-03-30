import os, sys
from os.path import abspath, dirname, isdir, isfile, join

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from unittest import skip

import requests_mock
import json

from django.test import Client, tag, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import ManifestTestParams
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataverses.dataverse_request_handler import DataverseRequestHandler
from opendp_apps.user.models import DataverseUser
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler.tasks import ProfileHandler
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.dataset.models import DataSetInfo
from django.core.serializers.json import DjangoJSONEncoder


class ProfilerTest(TestCase):

    fixtures = ['test_profiler_data_001.json']

    def setUp(self):
        """Used for multiple tests"""
        self.ds_01_object_id = "9255c067-e435-43bd-8af1-33a6987ffc9b"
        """
        # test client
        self.client = Client()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        self.client.force_login(self.user_obj)

        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()
        """

    def test_010_profile_good_file(self):
        """(10) Profile file directory"""
        msgt(self.test_010_profile_good_file.__doc__)

        # File to profile
        #
        filepath = join(TEST_DATA_DIR, 'fearonLaitin.csv')
        print('filepath', filepath)
        self.assertTrue(isfile(filepath))

        # Retrieve DataSetInfo, save the file to this object
        #
        dsi = DataSetInfo.objects.get(object_id=self.ds_01_object_id)

        # Run profiler
        #
        profiler = profiler_tasks.run_profile_by_filepath(filepath, dsi.object_id)

        # Shouldn't have errors
        if profiler.has_error():
            print(f'!! error: {profiler.get_err_msg()}')

        self.assertTrue(profiler.has_error() is False)
        profile_json_str1 = json.dumps(profiler.data_profile, cls=DjangoJSONEncoder, indent=4)

        # Re-retrieve object and data profile
        dsi = DataSetInfo.objects.get(object_id=dsi.object_id)
        info = dsi.data_profile_as_dict()
        profile_json_str2 = json.dumps(info, cls=DjangoJSONEncoder, indent=4)

        self.assertTrue(profile_json_str1, profile_json_str2)

