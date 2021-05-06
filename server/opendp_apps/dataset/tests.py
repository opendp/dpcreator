from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APITestCase

from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataset.models import DataSetInfo

class TestDataSetSerializer(APITestCase):

    def setUp(self) -> None:
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')
        self.client.force_login(self.user_obj)

    def test_successful_get(self):
        """(10) Get inheritors of DataSetInfo"""
        msgt(self.test_successful_get.__doc__)
        response = self.client.get(reverse("datasetinfo-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'count': 0, 'next': None, 'previous': None, 'results': []})

    def test_unsuccessful_get(self):
        """(15) Fail to get DataSetInfo"""
        msgt(self.test_unsuccessful_get.__doc__)
        self.client.logout()
        response = self.client.get(reverse("datasetinfo-list"))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(), {'detail': 'Authentication credentials were not provided.'})

    def test_successful_post(self):
        """(20) Create new inheritor of DataSetInfo"""
        msgt(self.test_successful_post.__doc__)
        response = self.client.post(reverse("datasetinfo-list"), {'resourcetype': 'DataSetInfo',
                                                                  'name': 'test',
                                                                  'creator': self.user_obj.username,
                                                                  'source': 'upload'})

        resp_json = response.json()

        expected_resp = {"creator": "dv_depositor",
                         "name": "test",
                         "object_id": resp_json['object_id'],   # object_id value is dynamic
                         "resourcetype": DataSetInfo.__name__,
                         "source": "upload",
                         "status": DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED,
                         "status_name": DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED.label}

        self.assertEqual(resp_json, expected_resp)

        self.assertEqual(response.status_code, 201)

    def test_unsuccessful_post(self):
        """(25) Create new inheritor of DataSetInfo"""
        msgt(self.test_unsuccessful_post.__doc__)
        response = self.client.post(reverse("datasetinfo-list"), {'resourcetype': 'not a valid resourcetype',
                                                                  'name': 'test',
                                                                  'creator': self.user_obj.username,
                                                                  'source': 'not a valid source'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'resourcetype': 'Invalid resourcetype'})
