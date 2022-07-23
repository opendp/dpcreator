from http import HTTPStatus
from os.path import abspath, dirname, join
import uuid

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest
from opendp_apps.model_helpers.msg_util import msgt

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class TestFileUpload(BaseEndpointTest):

    fixtures = ['test_dataset_data_001.json', ]
    maxDiff = None

    def setUp(self):
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        self.test_file_name = 'Fatigue_data.tab'

        test_file = join(TEST_DATA_DIR, self.test_file_name)
        self.test_file_obj = SimpleUploadedFile(self.test_file_name,
                                                open(test_file, 'rb').read(),
                                                content_type="text/tab-separated-values")

        self.client.force_login(self.user_obj)

    def test_10_file_upload_api(self):
        """(10) Test File Upload API"""
        msgt(self.test_10_file_upload_api.__doc__)

        upload_name = 'Fatigue Direct Upload'

        payload = dict(name=upload_name,
                       creator=self.user_obj.object_id,
                       source_file=self.test_file_obj)

        upload_url = '/api/direct-upload/' # reverse("direct-upload-create")

        resp = self.client.post(upload_url,
                                data=payload)

        print('resp', resp.json())
        print('status code', resp.status_code)

        self.assertEqual(resp.status_code, HTTPStatus.CREATED)

        jresp = resp.json()
        self.assertEqual(jresp['creator'], str(self.user_obj.object_id))
        self.assertEqual(jresp['name'], upload_name)

    def test_20_file_upload_bad_user_id(self):
        """(20) Test File Upload API - bad user id"""
        msgt(self.test_20_file_upload_bad_user_id.__doc__)

        bad_user_id = uuid.uuid4()

        payload = dict(name='Fatigue Direct Upload',
                       creator=bad_user_id,
                       source_file=self.test_file_obj)

        upload_url = reverse("direct-upload-list")

        resp = self.client.post(upload_url,
                                data=payload)

        print('resp', resp.json())
        print('status code', resp.status_code)

        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)

        """
        Expected response: {'creator': 
            ['Object with object_id=a936f43f-e90a-4584-8f3e-4f03d5f1f704 does not exist.']}
        """
        jresp = resp.json()
        self.assertTrue('creator' in jresp)
        self.assertTrue(jresp['creator'][0].find('does not exist') > -1)

    def test_30_file_upload_delete(self):
        """
        Create a file upload and then delete it via the API
        :return:
        """
        payload = dict(name='Fatigue Direct Upload',
                       creator=self.user_obj.object_id,
                       source_file=self.test_file_obj)

        direct_upload_url = '/api/direct-upload/'

        resp = self.client.post(direct_upload_url,
                                data=payload)
        object_id = resp.json().get('object_id')
        response = self.client.delete(f'{direct_upload_url}{object_id}/')
        self.assertEqual(response.status_code, 204)
