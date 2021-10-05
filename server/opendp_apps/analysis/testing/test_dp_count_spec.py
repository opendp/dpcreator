from os.path import abspath, dirname, isdir, isfile, join

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from unittest import skip

import json
import decimal

from django.contrib.auth import get_user_model
from django.test.testcases import TestCase

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.dataset.models import DataSetInfo

from unittest import skip
from opendp_apps.analysis.tools.dp_count_spec import DPCountSpec

from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.analysis import static_vals as astatic

from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils.extra_validators import *


#    VALIDATE_MSG_ZERO_OR_GREATER, VALIDATE_MSG_EPSILON


class DPCountStatSpecTest(TestCase):
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


    def test_10_count_valid_spec(self):
        """(10) Run DP Count valid spec, float column"""
        msgt(self.test_10_count_valid_spec.__doc__)

        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': astatic.DP_COUNT,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_99,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '182',
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'type': 'Float', },
                      }

        dp_count = DPCountSpec(spec_props)
        dp_count.is_chain_valid()
        #if dp_count.has_error():
        #    print(dp_count.get_err_msgs())

        # ------------------------------------------------------
        # Run the actual count
        # ------------------------------------------------------
        # Column indexes - We know this data has 20 columns
        col_indexes = [idx for idx in range(0, 20)]

        # File object
        #
        eye_fatigue_filepath = join(TEST_DATA_DIR, 'Fatigue_data.tab')
        # print('eye_fatigue_filepath', eye_fatigue_filepath)
        self.assertTrue(isfile(eye_fatigue_filepath))

        file_obj = open(eye_fatigue_filepath, 'r')

        # Call run_chain
        #
        dp_count.run_chain(col_indexes, file_obj, sep_char="\t")
        file_obj.close()

        self.assertFalse(dp_count.has_error())

        # val from local machine: 4.6051702036798
        #self.assertTrue(dp_count.accuracy_val > 4.5)
        #self.assertTrue(dp_count.accuracy_val < 4.7)

        # Actual count 184
        self.assertTrue(dp_count.value > 170) # should be well within range

        return
        # Call run_chain
        #
        count_vals = []
        for x in range(100):
            print(f'\n>> Run {x+1}')
            file_obj = open(eye_fatigue_filepath, 'r')
            dp_count.run_chain(col_indexes, file_obj, sep_char="\t")
            file_obj.close()
            count_vals.append(dp_count.value)

        count_vals.sort()
        print('count_vals', count_vals)

        print('Actual count: 183')


    def test_20_count_valid_spec(self):
        """(20) Run DP Count valid spec, string column"""
        msgt(self.test_20_count_valid_spec.__doc__)

        spec_props = {'variable': 'age',
                      'col_index': 1,
                      'statistic': astatic.DP_COUNT,
                      'dataset_size': 10_000,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '44',
                      'variable_info': {'min': 18,
                                        'max': 95,
                                        'type': pstatic.VAR_TYPE_INTEGER},
                      }

        dp_count = DPCountSpec(spec_props)
        self.assertTrue(dp_count.is_chain_valid())
        # if dp_count.has_error():
        #    print(dp_count.get_err_msgs())
        self.assertFalse(dp_count.has_error())

        # ------------------------------------------------------
        # Run the actual count
        # ------------------------------------------------------
        # Column indexes - We know this data has 11 columns
        col_indexes = [idx for idx in range(0, 11)]

        # File object
        #
        pums_extract_10_000 = join(TEST_DATA_DIR, 'PUMS5extract10000.csv')
        # print('eye_fatigue_filepath', eye_fatigue_filepath)
        self.assertTrue(isfile(pums_extract_10_000))

        file_obj = open(pums_extract_10_000, 'r')

        # Call run_chain
        #
        dp_count.run_chain(col_indexes, file_obj, sep_char=",")
        file_obj.close()

        self.assertFalse(dp_count.has_error())

        # val from local machine: 2.9957322850627124
        self.assertTrue(dp_count.accuracy_val > 2.995)
        self.assertTrue(dp_count.accuracy_val < 2.996)

        # Actual count 10_000
        self.assertTrue(dp_count.value > 9_980) # should be well within range

        final_dict = dp_count.get_release_dict()
        self.assertIn('description', final_dict)
        self.assertIn('text', final_dict['description'])
        self.assertIn('html', final_dict['description'])

        #print(json.dumps(dp_count.get_release_dict(), indent=4))
        return
        # Call run_chain "num_runs" times
        #
        num_runs = 100
        count_vals = []
        for x in range(num_runs):
            print(f'\n>> Run {x+1}')
            file_obj = open(pums_extract_10_000, 'r')
            dp_count.run_chain(col_indexes, file_obj, sep_char=",")
            file_obj.close()
            count_vals.append(dp_count.value)

        count_vals.sort()
        print('count_vals', count_vals)
        print('Actual count: 10,000')

