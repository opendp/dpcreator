from os.path import abspath, dirname, isfile, join

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_sum_spec import DPSumSpec
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.utils.extra_validators import VALIDATE_MSG_NOT_INT

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from unittest import skip


@skip('Reconfiguring for analyst mode')
class DPSumStatSpecTest(StatSpecTestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def test_05_valid_noise_mechanism(self):
        """(5) Check for the correct noise_mechanism"""
        msgt(self.test_05_valid_noise_mechanism.__doc__)
        dp_sum = DPSumSpec({})
        self.assertEqual(dp_sum.noise_mechanism, astatic.NOISE_LAPLACE_MECHANISM)

    def test_10_sum_valid_spec(self):
        """(10) Run DP Sum valid spec, float column"""
        msgt(self.test_10_sum_valid_spec.__doc__)

        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': astatic.DP_SUM,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'cl': astatic.CL_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '0',
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'type': pstatic.VAR_TYPE_FLOAT},
                      }

        dp_sum = DPSumSpec(spec_props)
        valid = dp_sum.is_chain_valid()
        if dp_sum.has_error():
            print(f"Error messages: {dp_sum.get_err_msgs()}")
        self.assertTrue(valid)

        # ------------------------------------------------------
        # Run the actual sum
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
        dp_sum.run_chain(col_indexes, file_obj, sep_char="\t")
        file_obj.close()

        self.assertFalse(dp_sum.has_error())

        # Actual sum -173.920535743
        self.assertTrue(dp_sum.value > -250)  # should be well within range

        # import json
        # print(json.dumps(dp_sum.get_release_dict(), indent=4))

    def test_20_sum_valid_spec(self):
        """(20) Run DP Sum valid spec, integer column"""
        msgt(self.test_20_sum_valid_spec.__doc__)

        spec_props = {'variable': 'age',
                      'col_index': 4,
                      'statistic': astatic.DP_SUM,
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

        dp_sum = DPSumSpec(spec_props)
        if dp_sum.has_error():
            print(dp_sum.get_err_msgs())

        self.assertTrue(dp_sum.is_chain_valid())
        self.assertFalse(dp_sum.has_error())

        # ------------------------------------------------------
        # Run the actual sum
        # ------------------------------------------------------
        # Column indexes - We know this data has 11 columns
        col_indexes = [idx for idx in range(0, 11)]

        pums_extract_10_000 = join(TEST_DATA_DIR, 'PUMS5extract10000.csv')
        self.assertTrue(isfile(pums_extract_10_000))

        file_obj = open(pums_extract_10_000, 'r')

        # Call run_chain
        #
        dp_sum.run_chain(col_indexes, file_obj, sep_char=",")
        file_obj.close()

        self.assertFalse(dp_sum.has_error())

        # val from local machine: 230.67138507795602
        self.assertTrue(dp_sum.accuracy_val > 230.6)
        self.assertTrue(dp_sum.accuracy_val < 230.7)

        # Actual sum 444850
        self.assertTrue(dp_sum.value > 400_000)  # should be well within range

        final_dict = dp_sum.get_release_dict()
        self.assertIn('description', final_dict)
        self.assertIn('text', final_dict['description'])
        self.assertIn('html', final_dict['description'])

    def test_30_sum_invalid_type_categorical(self):
        """(30) Run DP Sum invalid spec, categorical column"""
        msgt(self.test_30_sum_invalid_type_categorical.__doc__)

        spec_props = {'variable': 'age',
                      'col_index': 4,
                      'statistic': astatic.DP_SUM,
                      'dataset_size': 10_000,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'cl': astatic.CL_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '44',
                      'variable_info': {'min': 18,
                                        'max': 95,
                                        'type': pstatic.VAR_TYPE_CATEGORICAL},
                      }

        dp_sum = DPSumSpec(spec_props)
        # if dp_sum.has_error():
        #    print(dp_sum.get_err_msgs())

        self.assertFalse(dp_sum.is_chain_valid())
        self.assertTrue(dp_sum.get_single_err_msg().find(pstatic.ERR_MSG_VAR_TYPE_NOT_NUMERIC) > -1)

    def test_40_sum_invalid_dataset_size(self):
        """(40) Run DP Sum invalid spec, bad dataset size"""
        msgt(self.test_40_sum_invalid_dataset_size.__doc__)

        spec_props = {'variable': 'age',
                      'col_index': 4,
                      'statistic': astatic.DP_SUM,
                      'dataset_size': 'potato',
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'cl': astatic.CL_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '44',
                      'variable_info': {'min': 18,
                                        'max': 95,
                                        'type': pstatic.VAR_TYPE_INTEGER},
                      }

        dp_sum = DPSumSpec(spec_props)
        # if dp_sum.has_error():
        #    print(dp_sum.get_err_msgs())

        self.assertFalse(dp_sum.is_chain_valid())
        self.assertTrue(dp_sum.get_single_err_msg().find(VALIDATE_MSG_NOT_INT) > -1)
        self.assertTrue(dp_sum.get_single_err_msg().find('dataset_size') > -1)
