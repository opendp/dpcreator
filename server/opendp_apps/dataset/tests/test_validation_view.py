from django.contrib.auth import get_user_model
from django.test.testcases import TestCase
from rest_framework.test import APIClient

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.msg_util import msgt


class TestValidationView(TestCase):

    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):
        self.client = APIClient()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        self.client.force_login(self.user_obj)

        self.request = {
            "analysis_plan_id": 0,
            "dp_statistics": [{
                "error": "",
                "label": "EyeHeight",
                "locked": False,
                "epsilon": 0.0625,
                "variable": "eyeHeight",
                "statistic": "mean",
                "fixed_value": "5",
                "handle_as_fixed": True,
                "missing_values_handling": "insert_fixed"
            }]
        }

    def test_post_fail_not_logged_in(self):
        """Test post not logged in"""
        msgt(self.test_post_fail_not_logged_in.__doc__)

        client = APIClient()
        dataset_info = DataSetInfo.objects.get(id=4)
        AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        analysis_plan = AnalysisPlan.objects.first()
        self.request['analysis_plan_id'] = analysis_plan.object_id
        response = client.post('/api/validation/', data=self.request, format='json')
        self.assertEqual(response.status_code, 400)

    def test_post_success(self):
        """Test post logged in"""
        msgt(self.test_post_success.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)
        AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        analysis_plan = AnalysisPlan.objects.first()
        self.request['analysis_plan_id'] = analysis_plan.object_id
        response = self.client.post('/api/validation/', data=self.request, format='json')
        self.assertEqual(response.status_code, 200)
