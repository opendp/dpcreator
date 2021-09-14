from django.test.testcases import TestCase

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis import static_vals as astatic
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
                    "statistic": astatic.DP_MEAN,
                    "variable": "EyeHeight",
                    "epsilon": 1,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"
                },
                {
                    "statistic": astatic.DP_SUM,
                    "variable": "EyeHeight",
                    "epsilon": 1,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"
                }
            ]
        }

    def test_save(self):
        """Test the ReleaseValidationSerializer"""
        msgt(self.test_save.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)

        # Create a plan
        #
        plan_info = AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        self.assertTrue(plan_info.success)
        orig_plan = plan_info.data

        # Retrieve it
        #
        analysis_plan = AnalysisPlan.objects.first()
        self.assertEqual(orig_plan.object_id, analysis_plan.object_id)

        # Send the dp_statistics for validation
        #
        self.request['analysis_plan_id'] = analysis_plan.object_id

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=self.request)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        print('stats_valid', stats_valid)
        expected_result =  [\
            {'var_name': 'EyeHeight', 'statistic': 'mean', 'valid': True, 'message': None},
            {'var_name': 'EyeHeight', 'statistic': 'sum', 'valid': False,
             'message': 'Statistic "sum" will be supported soon!'}]
        self.assertEqual(expected_result, stats_valid)
