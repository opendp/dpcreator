from os.path import abspath, dirname, join

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status

from opendp_apps.model_helpers.msg_util import msgt

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class ReleaseSchemasTest(TestCase):
    fixtures = ['schema_fixture_v0-2-0.json']

    VERSION_0_2_0 = '0.2.0'
    JSON_SCHEMA_URL = 'https://json-schema.org/draft/2020-12/schema'

    def setUp(self):
        # super().setUp()

        self.API_SCHEMA_PREFIX = '/api/schema/'

        # Create a OpenDP User object
        #
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dp_depositor')

    def check_basic_schema_fields(self, json_info, semantic_version):
        """Check basic fields"""
        self.assertTrue(type(json_info) is dict)
        self.assertTrue(type(semantic_version) is str)

        self.assertEqual(json_info['version'], semantic_version)
        self.assertEqual(json_info['$schema'], self.JSON_SCHEMA_URL)
        self.assertTrue(json_info['$id'].endswith(semantic_version + '/'))

    def test_010_retrieve_plan_list(self):
        """(10) Retrieve schema via API, using list"""
        msgt(self.test_010_retrieve_plan_list.__doc__)

        response = self.client.get(self.API_SCHEMA_PREFIX,
                                   content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_info = response.json()
        self.assertEqual(json_info['count'], 1)
        self.check_basic_schema_fields(json_info['results'][0], self.VERSION_0_2_0)

    def test_020_retrieve_plan_by_version(self):
        """(20) Retrieve schema via API, using version number"""
        msgt(self.test_020_retrieve_plan_by_version.__doc__)

        schema_url = f'{self.API_SCHEMA_PREFIX}{self.VERSION_0_2_0}/'
        response = self.client.get(schema_url,
                                   content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        json_info = response.json()
        self.check_basic_schema_fields(response.json(), self.VERSION_0_2_0)

    def test_030_retrieve_plan_by_latest(self):
        """(30) Retrieve schema via API, using 'latest/' """
        msgt(self.test_030_retrieve_plan_by_latest.__doc__)

        schema_url = f'{self.API_SCHEMA_PREFIX}latest/'
        response = self.client.get(schema_url,
                                   content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.check_basic_schema_fields(response.json(), self.VERSION_0_2_0)
