import json
from unittest import skip
import tempfile
import requests_mock

from django.test import Client, tag, TestCase
from django.urls import reverse

from django.conf import settings
from django.template.loader import render_to_string

from django.contrib.auth import get_user_model
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import ManifestTestParams, DataverseHandoff, RegisteredDataverse
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataverses.dataverse_request_handler import DataverseRequestHandler
from opendp_apps.user.models import DataverseUser, OpenDPUser
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.model_helpers.msg_util import msgt

TAG_WEB_CLIENT = 'web-client' # skip these tests on travis; need to fix as many use requests to access the localhost


class DataverseEndpointTest(TestCase):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                # This file needs a real token in order to run tests
                'test_dataverse_handoff_01.json']

    def setUp(self):

        # test client
        self.client = Client()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        self.client.force_login(self.user_obj)

        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()

    def test_successful_creation(self):
        url = reverse('dv-user')
        response = self.client.post(url, data={'user_id': 1, 'dataverse_id': 1})
        self.assertEqual(response.status_code, 201)

    def test_user_not_found(self):
        url = reverse('dv-user')
        response = self.client.post(url, data={'user_id': 0, 'dataverse_id': 1})
        self.assertEqual(response.status_code, 404)

    def test_dataverse_handoff_not_found(self):
        url = reverse('dv-user')
        response = self.client.post(url, data={'user_id': 1, 'dataverse_id': 0})
        self.assertEqual(response.status_code, 404)

    def test_invalid_site_url(self):
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.siteUrl = 'www.invalidsite.com'
        dataverse_handoff.save()
        url = reverse('dv-user')
        response = self.client.post(url, data={'user_id': 1, 'dataverse_id': 1})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(json.loads(response.content)['error'], 'Site www.invalidsite.com is not valid')

    def test_invalid_token(self):
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.apiGeneralToken = 'invalid_token_1234'
        dataverse_handoff.save()
        url = reverse('dv-user')
        response = self.client.post(url, data={'user_id': 1, 'dataverse_id': 0})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.content)['detail'], 'Not found.')
