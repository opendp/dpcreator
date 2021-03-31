import json

from django.test import TestCase
from rest_framework.test import APIClient


class TestDataverseFileView(TestCase):

    client = APIClient()
    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                # This file needs a real token in order to run tests
                'test_dataverse_handoff_01.json',
                'test_opendp_users_01.json',
                'test_dataverse_user_01.json']

    def test_list(self):
        # Example UUID: "cef0cbf3-6458-4f13-a418-ee4d7e7505dd"
        response = self.client.get('/api/dv-file/', data={'handoff_id': 1, 'user_id': 1})
        # print(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.json().get('id'), 1)
        self.assertEquals(response.json().get('dv_installation'), 1)

