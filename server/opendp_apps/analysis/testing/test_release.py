from os.path import abspath, dirname, isdir, isfile, join

from opendp_apps.analysis.serializers import ComputationChainSerializer

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from unittest import skip

import json
from django.contrib.auth import get_user_model
from django.core.files import File
from django.test.testcases import TestCase

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.dataset.models import DataSetInfo

from unittest import skip
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis.tools.dp_mean_spec import DPMeanSpec

from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.analysis import static_vals as astatic

from opendp_apps.model_helpers.msg_util import msgt





class ReleaseTest(TestCase):

    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):
        """Make a user"""
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

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

    @skip
    def test_10_release_mean(self):
        """(10) Test DP Mean Spec"""
        msgt(self.test_10_release_mean.__doc__)

        analysis_plan = self.retrieve_new_plan()

        # Send the dp_statistics for validation
        #
        stat_spec =  {
            "statistic": astatic.DP_MEAN,
            "variable": "eyeHeight",
            "epsilon": 1,
            "delta": 0,
            "ci": astatic.CI_95,
            "error": "",
            "impute_constant": 0.0,
            "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
            "handle_as_fixed": False,
            "fixed_value": "5.0",
            "locked": False,
            "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ComputationChainSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_info = serializer.save(**dict(opendp_user=self.user_obj))
        #print('stats_info.success', stats_info.success)
        self.assertTrue(stats_info.success)

        expected_result = [{'variable': 'EyeHeight', 'statistic': 'mean', 'valid': True,
                            'message': None,
                            'accuracy': {
                                'val': 1.6370121873967791,
                                'message': 'Releasing mean for the variable EyeHeight. With at least probability 0.95 the output mean will differ from the true mean by at most 1.6370121873967791 units. Here the units are the same units the variable has in the dataset.'}}]

        #print('stats_info.data', stats_info.data)
        self.assertEqual(stats_info.data[0]['valid'], True)

        # Were accuracy results included?
        self.assertTrue('val' in stats_info.data[0]['accuracy'])
        self.assertTrue('message' in stats_info.data[0]['accuracy'])

        accuracy_msg = f'output {astatic.DP_MEAN} will differ from the true {astatic.DP_MEAN} by at'
        self.assertTrue(stats_info.data[0]['accuracy']['message'].find(accuracy_msg) > -1)
