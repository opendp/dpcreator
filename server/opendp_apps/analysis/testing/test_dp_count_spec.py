import json
from os.path import abspath, dirname, isfile, join
from unittest import skip

from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_count_spec import DPCountSpec
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils.extra_validators import *

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


@skip('Reconfiguring for analyst mode')
class DPCountStatSpecTest(StatSpecTestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def test_05_valid_noise_mechanism(self):
        """Check for the correct noise_mechanism"""
        dp_count = DPCountSpec({})
        self.assertEqual(dp_count.noise_mechanism, astatic.NOISE_GEOMETRIC_MECHANISM)

    def test_10_count_valid_spec(self):
        """(10) Run DP Count valid spec, float column"""
        msgt(self.test_10_count_valid_spec.__doc__)

        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': astatic.DP_COUNT,
                      'epsilon': 1.0,
                      'cl': astatic.CL_99,
                      'variable_info': {
                          'type': pstatic.VAR_TYPE_FLOAT
                      },
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

    def test_20_count_valid_spec(self):
        """(20) Run DP Count valid spec, integer column"""
        msgt(self.test_20_count_valid_spec.__doc__)

        spec_props = {'variable': 'age',
                      'col_index': 1,
                      'statistic': astatic.DP_COUNT,
                      'epsilon': 1.0,
                      'cl': astatic.CL_95,
                      'variable_info': {'type': pstatic.VAR_TYPE_INTEGER},
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
        self.assertTrue(dp_count.value > 9_980)  # should be well within range

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
                      'epsilon': 1.0,
                      'cl': astatic.CL_99,
                      'variable_info': {
                          'type': pstatic.VAR_TYPE_FLOAT
                      },
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

    def test_40_count_valid_str_spec(self):
        """(40) Run DP Count string"""
        msgt(self.test_40_count_valid_str_spec.__doc__)

        spec_props = {'variable': 'Subject',
                      'col_index': 0,
                      'statistic': astatic.DP_COUNT,
                      'epsilon': 1.0,
                      'cl': astatic.CL_95,
                      'variable_info': {'type': pstatic.VAR_TYPE_CATEGORICAL},
                      }

        dp_count = DPCountSpec(spec_props)
        dp_count.is_chain_valid()
        self.assertTrue(dp_count.is_chain_valid())
        # if dp_count.has_error():
        #    print(dp_count.get_err_msgs())
        self.assertFalse(dp_count.has_error())

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
        self.show_release_result(dp_count.get_release_dict())

        # (test has wide accuracy latitude)
        self.assertTrue(dp_count.accuracy_val > 2)
        self.assertTrue(dp_count.accuracy_val < 4)

        final_dict = dp_count.get_release_dict()
        self.assertIn('description', final_dict)
        self.assertIn('text', final_dict['description'])
        self.assertIn('html', final_dict['description'])

    def test_50_count_missing_vals_str(self):
        """(50) Run DP Count string"""
        msgt(self.test_50_count_missing_vals_str.__doc__)

        # right from UI, many of these fields (e.g. dataset_size, missing_values_handling, etc., are ignored)
        spec_props = {'error': '',
                      'label': 'gender',
                      'locked': False,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'cl': 0.95,
                      'variable': 'gender',
                      'statistic': 'count',
                      'fixed_value': 'male',
                      'handle_as_fixed': True,
                      'missing_values_handling': 'insert_fixed',
                      'dataset_size': 1000,
                      'variable_info': {
                          'name': 'gender',
                          'type': pstatic.VAR_TYPE_CATEGORICAL,
                          'label': 'gender',
                          'selected': True,
                          'categories': ['Genderfluid'],
                          'sort_order': 4},
                      'col_index': 4}

        dp_count = DPCountSpec(spec_props)
        dp_count.is_chain_valid()
        self.assertTrue(dp_count.is_chain_valid())
        # if dp_count.has_error():
        #    print(dp_count.get_err_msgs())

        # ------------------------------------------------------
        # Run the actual count
        # ------------------------------------------------------
        # Column indexes - We know this data has 20 columns
        col_indexes = [idx for idx in range(0, 28)]

        # File object
        #
        bonabo_filepath = join(TEST_DATA_DIR, 'bonabo MOCK_DATA.csv')
        # print('eye_fatigue_filepath', eye_fatigue_filepath)
        self.assertTrue(isfile(bonabo_filepath))

        file_obj = open(bonabo_filepath, 'r')

        # Call run_chain
        #
        dp_count.run_chain(col_indexes, file_obj, sep_char=",")
        file_obj.close()

        self.assertFalse(dp_count.has_error())

        # val from local machine: 4.6051702036798
        # self.assertTrue(dp_count.accuracy_val > 4.5)
        # self.assertTrue(dp_count.accuracy_val < 4.7)

        # Actual count 184
        self.assertTrue(dp_count.value > 970)  # should be well within range

    def test_60_count_missing_vals_bool(self):
        """(60) Run DP Count bool"""
        msgt(self.test_60_count_missing_vals_bool.__doc__)

        spec_props = {'variable': 'Boolean2',
                      'col_index': 8,
                      'statistic': astatic.DP_COUNT,
                      'epsilon': 1.0,
                      'cl': astatic.CL_95,
                      'variable_info': {'type': pstatic.VAR_TYPE_BOOLEAN},
                      }

        dp_count = DPCountSpec(spec_props)
        dp_count.is_chain_valid()
        self.assertTrue(dp_count.is_chain_valid())
        # if dp_count.has_error():
        #    print(dp_count.get_err_msgs())

        # ------------------------------------------------------
        # Run the actual count
        # ------------------------------------------------------
        # Column indexes - We know this data has 20 columns
        col_indexes = [idx for idx in range(0, 28)]

        # File object
        #
        bonabo_filepath = join(TEST_DATA_DIR, 'bonabo MOCK_DATA.csv')
        # print('eye_fatigue_filepath', eye_fatigue_filepath)
        self.assertTrue(isfile(bonabo_filepath))

        file_obj = open(bonabo_filepath, 'r')

        # Call run_chain
        #
        dp_count.run_chain(col_indexes, file_obj, sep_char=",")
        file_obj.close()

        self.assertFalse(dp_count.has_error())

        # val from local machine: 4.6051702036798
        # self.assertTrue(dp_count.accuracy_val > 4.5)
        # self.assertTrue(dp_count.accuracy_val < 4.7)

        # Actual count 184
        self.assertTrue(dp_count.value > 970)  # should be well within range

    def show_release_result(self, release_dict: {}):
        """print the result to the screen"""
        print(json.dumps(release_dict, indent=4))
