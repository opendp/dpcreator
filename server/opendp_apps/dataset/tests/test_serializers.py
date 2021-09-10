from django.test.testcases import TestCase

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis.serializers import ReleaseInfoSerializer
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.msg_util import msgt


class TestReleaseInfoSerializer(TestCase):

    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):
        # test client
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

    def test_save(self):
        msgt(self.test_save.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)

        resp = AnalysisPlanUtil.create_plan(dataset_info.object_id,
                                            self.user_obj)
        analysis_plan = AnalysisPlan.objects.first()
        self.request['analysis_plan_id'] = analysis_plan.object_id
        serializer = ReleaseInfoSerializer(data=self.request)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})
        stats_valid = serializer.save()
        self.assertEqual([{'valid': True}], stats_valid)
