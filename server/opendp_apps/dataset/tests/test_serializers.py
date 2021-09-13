from django.test.testcases import TestCase

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis.serializers import ReleaseValidationSerializer
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
            "analysis_plan_id": "98f5ec0d-33ae-45e2-af0e-125276376ef2",
            "dp_statistics": [
                {
                    "statistic": "mean",
                    "variable": "eye_height",
                    "epsilon": 1,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": "insert_fixed",
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"
                }
            ]
        }

    def test_save(self):
        msgt(self.test_save.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)

        AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        analysis_plan = AnalysisPlan.objects.first()
        self.request['analysis_plan_id'] = analysis_plan.object_id
        serializer = ReleaseValidationSerializer(data=self.request)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})
        stats_valid = serializer.save()
        self.assertEqual([{'valid': True}], stats_valid)
