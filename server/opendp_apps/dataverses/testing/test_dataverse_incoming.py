import json
from unittest import skip
import tempfile

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model

from opendp_apps.dataverses.models import ManifestTestParams
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.model_helpers.msg_util import msgt


class DataverseIncomingTest(TestCase):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json']

    def setUp(self):

        # test client
        self.client = Client()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        self.client.force_login(self.user_obj)


    def test_010_dv_params(self):
        """(10) Basic check of incoming DV params"""
        msgt(self.test_010_dv_params.__doc__)

        print('1. Retrieve mock params')
        test_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()
        self.assertTrue(test_params is not None)

        print('2. Area all params there? (should be yes)')
        params_dict = test_params.as_dict()
        dv_manifest = DataverseManifestParams(params_dict)
        self.assertTrue(dv_manifest.has_error() is False)

        print('3. Test with missing param. fileId')
        params_dict.pop('fileId')
        dv_manifest = DataverseManifestParams(params_dict)
        self.assertTrue(dv_manifest.has_error())
        self.assertTrue(dv_manifest.get_error_message().find('required parameter is missing') > -1)
        print(dv_manifest.get_error_message())

