from django.test.testcases import TestCase

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.serializers import ReleaseValidationSerializer
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils.extra_validators import \
    (VALIDATE_MSG_EPSILON,)


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
                    "variable": "BlinkDuration",
                    "epsilon": 1.0,
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

    def retrieve_new_plan(self):
        """Convenience method to create a new plan"""

        # Create a plan
        #
        dataset_info = DataSetInfo.objects.get(id=4)

        plan_info = AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        self.assertTrue(plan_info.success)
        orig_plan = plan_info.data

        # Retrieve it
        #
        analysis_plan = AnalysisPlan.objects.first()
        self.assertEqual(orig_plan.object_id, analysis_plan.object_id)

        return analysis_plan

    def test_10_validate_stats(self):
        """(10) Test a working stat"""
        msgt(self.test_10_validate_stats.__doc__)

        analysis_plan = self.retrieve_new_plan()

        # Send the dp_statistics for validation
        #
        self.request['analysis_plan_id'] = analysis_plan.object_id
        stat_spec =  { \
                "statistic": astatic.DP_MEAN,
                "variable": "EyeHeight",
                "epsilon": 1,
                "delta": 0,
                "error": "",
                "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                "handle_as_fixed": False,
                "fixed_value": "5.0",
                "locked": False,
                "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        print('stats_valid', stats_valid)
        expected_result = [{'var_name': 'EyeHeight', 'statistic': astatic.DP_MEAN,
                            'valid': True, 'message': None}]

        self.assertEqual(expected_result, stats_valid)


    def test_20_fail_unsupported_stat(self):
        """(20) Fail: Test a known but unsupported statistic"""
        msgt(self.test_20_fail_unsupported_stat.__doc__)

        analysis_plan = self.retrieve_new_plan()

        # Send the dp_statistics for validation
        #
        self.request['analysis_plan_id'] = analysis_plan.object_id
        stat_spec =  { \
                    "statistic": astatic.DP_SUM,
                    "variable": "EyeHeight",
                    "epsilon": 1,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        print('stats_valid', stats_valid)
        expected_result = [ \
                {'var_name': 'EyeHeight', 'statistic': astatic.DP_SUM, 'valid': False,
                  'message': 'Statistic "sum" will be supported soon!'}]

        self.assertEqual(expected_result, stats_valid)



    def test_30_fail_bad_min_max(self):
        """(30) Fail: Add bad min/max values"""
        msgt(self.test_30_fail_bad_min_max.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_info_mod = analysis_plan.variable_info
        # invalid min/max
        variable_info_mod['TypingSpeed']['min'] = 120
        variable_info_mod['TypingSpeed']['max'] = 5
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        self.request['analysis_plan_id'] = analysis_plan.object_id
        stat_spec =  { \
                        "statistic": astatic.DP_MEAN,
                        "variable": "TypingSpeed",
                        "epsilon": 1,
                        "delta": 0,
                        "error": "",
                        "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                        "handle_as_fixed": False,
                        "fixed_value": "5.0",
                        "locked": False,
                        "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        print('stats_valid', stats_valid)
        expected_result = [ {'var_name': 'TypingSpeed', 'statistic': astatic.DP_MEAN,
                             'valid': False,
                             'message': 'lower bound may not be greater than upper bound'}]


        self.assertEqual(expected_result, stats_valid)



    def test_40_fail_exceed_epsilon(self):
        """(40) Fail: Exceed total epsilon"""
        msgt(self.test_40_fail_exceed_epsilon.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_info_mod = analysis_plan.variable_info
        # valid min/max
        variable_info_mod['BlinkDuration']['min'] = 1
        variable_info_mod['BlinkDuration']['max'] = 400
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        self.request['analysis_plan_id'] = analysis_plan.object_id
        stat_spec =  { \
                    "statistic": astatic.DP_MEAN,
                    "variable": "BlinkDuration",
                    "epsilon": 1.5,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        print('stats_valid', stats_valid)
        expected_result =  [{'var_name': 'BlinkDuration', 'statistic': astatic.DP_MEAN,
                             'valid': False,
                             'message': VALIDATE_MSG_EPSILON}]

        self.assertEqual(expected_result, stats_valid)



    def test_50_bad_total_epsilon(self):
        """(50) Fail: Bad total epsilon"""
        msgt(self.test_50_bad_total_epsilon.__doc__)

        analysis_plan = self.retrieve_new_plan()

        setup_info = analysis_plan.dataset.get_depositor_setup_info()
        setup_info.epsilon = 4
        setup_info.save()

        # Send the dp_statistics for validation
        #
        self.request['analysis_plan_id'] = analysis_plan.object_id
        stat_spec = { \
            "statistic": astatic.DP_MEAN,
            "variable": "EyeHeight",
            "epsilon": 1,
            "delta": 0,
            "error": "",
            "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
            "handle_as_fixed": False,
            "fixed_value": "5.0",
            "locked": False,
            "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        result = serializer.save(**dict(opendp_user=self.user_obj))
        print('stats_valid', result)

        self.assertTrue('message' in result)
        self.assertTrue(result['message'].find(astatic.ERR_MSG_BAD_TOTAL_EPSILON) > -1)



"""

           
            {'var_name': 'TypingSpeed', 'statistic': 'mean', 'valid': False,
             'message': 'lower bound may not be greater than upper bound'}]
   
     # Set bad min/max for a variable
        #
        variable_info_mod = analysis_plan.variable_info
        # invalid min/max
        variable_info_mod['TypingSpeed']['min'] = 120
        variable_info_mod['TypingSpeed']['max'] = 5
        # valid min/max
        variable_info_mod['BlinkDuration']['min'] = 1
        variable_info_mod['BlinkDuration']['max'] = 400
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()          
"""