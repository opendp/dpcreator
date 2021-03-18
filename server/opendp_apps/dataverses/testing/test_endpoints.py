import json
from unittest import skip

from django.test import Client, tag, TestCase
from django.urls import reverse

from django.contrib.auth import get_user_model
from opendp_apps.dataverses.models import ManifestTestParams, DataverseHandoff, RegisteredDataverse
from opendp_apps.user.models import DataverseUser, OpenDPUser

TAG_WEB_CLIENT = 'web-client' # skip these tests on travis; need to fix as many use requests to access the localhost


class BaseEndpointTest(TestCase):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                # This file needs a real token in order to run tests
                'test_dataverse_handoff_01.json',
                'test_opendp_users_01.json',
                'test_dataverse_user_01.json']

    def setUp(self):

        # test client
        self.client = Client()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        self.client.force_login(self.user_obj)

        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()


class DataversePostTest(BaseEndpointTest):

    def test_successful_creation(self):
        url = reverse('dv-user')
        print('test_successful_creation:', url)
        response = self.client.post(url, data={'user_id': 1, 'dataverse_id': 1})
        self.assertEqual(response.status_code, 201)

    def test_user_not_found(self):
        url = reverse('dv-user')
        print('test_successful_creation:', url)
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


class DataversePutTest(BaseEndpointTest):

    def test_successful_update(self):
        existing_dv_user = DataverseUser.objects.get(id=1)
        url = reverse('dv-user')
        response = self.client.put(url, data={'user_id': 1, 'dataverse_id': 1}, content_type='application/json')

        self.assertEqual(json.loads(response.content), {'dv_user': 1})
        self.assertEqual(response.status_code, 201)

        modified_dv_user = DataverseUser.objects.get(id=1)
        self.assertNotEqual(existing_dv_user.first_name, modified_dv_user.first_name)

    def test_user_not_found(self):
        url = reverse('dv-user')
        response = self.client.put(url, data={'user_id': 0, 'dataverse_id': 1}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_dataverse_handoff_not_found(self):
        url = reverse('dv-user')
        response = self.client.put(url, data={'user_id': 1, 'dataverse_id': 0}, content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_invalid_site_url(self):
        print('--- test_invalid_site_url ---')
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.siteUrl = 'www.invalidsite.com'
        dataverse_handoff.save()
        url = reverse('dv-user')
        response = self.client.put(url, data={"user_id": 1, "dataverse_id": 1}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_json = json.loads(response.content)
        self.assertEqual(response_json['error'], 'Site www.invalidsite.com is not valid')

    def test_invalid_token(self):
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.apiGeneralToken = 'invalid_token_1234'
        dataverse_handoff.save()
        url = reverse('dv-user')
        response = self.client.put(url, data={'user_id': 1, 'dataverse_id': 0}, content_type='application/json')
        response_json = json.loads(response.content)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['detail'], 'Not found.')
