import json
from os.path import abspath, dirname, isfile, join

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_count_spec import DPCountSpec
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.utils.extra_validators import *


class DPCountStatSpecTest(StatSpecTestCase):

    fixtures = ['test_dataset_data_001.json', ]

    def test_10_count_valid_spec(self):
        """(10) Run DP Count valid spec, float column"""
        msgt(self.test_10_count_valid_spec.__doc__)

        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': astatic.DP_COUNT,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'cl': astatic.CL_99,
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

    def test_20_count_valid_spec(self):
        """(20) Run DP Count valid spec, integer column"""
        msgt(self.test_20_count_valid_spec.__doc__)

        spec_props = {'variable': 'age',
                      'col_index': 1,
                      'statistic': astatic.DP_COUNT,
                      'dataset_size': 10_000,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'cl': astatic.CL_95,
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

        self.show_release_result(dp_count.get_release_dict())

        # val from local machine: 2.9957322850627124
        self.assertTrue(dp_count.accuracy_val > 2.995)
        self.assertTrue(dp_count.accuracy_val < 2.996)

        # Actual count 10_000
        self.assertTrue(dp_count.value > 9_980) # should be well within range

        final_dict = dp_count.get_release_dict()
        self.assertIn('description', final_dict)
        self.assertIn('text', final_dict['description'])
        self.assertIn('html', final_dict['description'])

    def test_30_count_valid_another_spec(self):
        """(30) Run DP Count on another valid spec"""
        msgt(self.test_30_count_valid_another_spec.__doc__)

        spec_props = {'variable': 'TypingSpeed',
                      'col_index': 5,
                      'statistic': astatic.DP_COUNT,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'cl': astatic.CL_99,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '62',
                      'variable_info': {'min': 1,
                                        'max': 61,
                                        'type': pstatic.VAR_TYPE_FLOAT},
                      }

        dp_count = DPCountSpec(spec_props)
        dp_count.is_chain_valid()
        # if dp_count.has_error():
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
        # self.assertTrue(dp_count.accuracy_val > 4.5)
        # self.assertTrue(dp_count.accuracy_val < 4.7)

        # Actual count 184
        self.assertTrue(dp_count.value > 170)  # should be well within range
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

        self.show_release_result(dp_count.get_release_dict())

        # (test has wide accuracy latitude)
        self.assertTrue(dp_count.accuracy_val > 4.4)
        self.assertTrue(dp_count.accuracy_val < 4.8)

        # Actual count 184
        self.assertTrue(dp_count.value > 170)  # should be well within range

        final_dict = dp_count.get_release_dict()
        self.assertIn('description', final_dict)
        self.assertIn('text', final_dict['description'])
        self.assertIn('html', final_dict['description'])

    def show_release_result(self, release_dict:{}):
        """print the result to the screen"""
        print(json.dumps(release_dict, indent=4))