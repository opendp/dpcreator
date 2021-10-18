import json
import decimal

from os.path import abspath, dirname, isfile, join

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_histogram_spec import DPHistogramSpec
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils.extra_validators import *


class HistogramStatSpecTest(StatSpecTestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def test_10_debug(self):
        """(10) Test DP Mean Spec"""
        msgt(self.test_10_debug.__doc__)

        spec_props = {'variable': 'Subject',
                      'col_index': 0,
                      'statistic': astatic.DP_HISTOGRAM,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      # 'accuracy': None,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': 0,
                      'variable_info': {'min': 0,
                                        'max': 100,
                                        'categories': ['"ac"', '"kj"', '"ys"', '"bh1"', '"bh2"', '"jm"', '"mh"', '"cw"',
                                                       '"jp"', '"rh"', '"aq"', '"ph"', '"le"', '"mn"', '"ls2"', '"no"',
                                                       '"af"'],
                                        'type': 'Integer', },
                      }

        dp_hist = DPHistogramSpec(spec_props)
        print('(1) Run initial check, before using the OpenDp library')
        print('  - Error found?', dp_hist.has_error())
        if dp_hist.has_error():
            print('\n-- Errors --')
            print(dp_hist.get_error_messages())
            print('\nUI info:', json.dumps(dp_hist.get_error_msg_dict()))
            return

        print('(2) Use the OpenDP library to check validity')
        print('  - Is valid?', dp_hist.is_chain_valid())
        if dp_hist.has_error():
            print('\n-- Errors --')
            print(dp_hist.get_error_messages())
            print('\nUI info:', json.dumps(dp_hist.get_error_msg_dict()))
        else:
            print('\n-- Looks good! --')
            print('\nUI info:', json.dumps(dp_hist.get_success_msg_dict()))

    def test_15_categorial_variables(self):
        """(15) Test DP Mean Spec with categorial variables"""
        msgt(self.test_15_categorial_variables.__doc__)

        spec_props = {
                'variable': 'Subject',
                'statistic': astatic.DP_HISTOGRAM,
                'dataset_size': 183,
                'epsilon': 1.0,
                'delta': 0.0,
                'ci': astatic.CI_95,
                'col_index': 0,
                'fixed_value': 1,
                'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                'variable_info': {
                    'min': 0,
                    'max': 1E5,
                    'categories': ['"ac"', '"kj"', '"ys"', '"bh1"', '"bh2"', '"jm"', '"mh"', '"cw"',
                                   '"jp"', '"rh"', '"aq"', '"ph"', '"le"', '"mn"', '"ls2"', '"no"', '"af"'],
                    'type': 'Categorical'
                }
            }

        dp_hist = DPHistogramSpec(spec_props)
        print('(1) Run initial check, before using the OpenDp library')
        print('  - Error found?', dp_hist.has_error())
        if dp_hist.has_error():
            print('\n-- Errors --')
            print(dp_hist.get_error_messages())
            print('\nUI info:', json.dumps(dp_hist.get_error_msg_dict()))
            return

        print('(2) Use the OpenDP library to check validity')
        print('  - Is valid?', dp_hist.is_chain_valid())
        if dp_hist.has_error():
            print('\n-- Errors --')
            print(dp_hist.get_error_messages())
            print('\nUI info:', json.dumps(dp_hist.get_error_msg_dict()))
        else:
            print('\n-- Looks good! --')
            print('\nUI info:', json.dumps(dp_hist.get_success_msg_dict()))

    def test_05_get_variable_order(self):
        """(05) Test get variable order"""
        msgt(self.test_05_get_variable_order.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_indices_info = analysis_plan.dataset.get_variable_order(as_indices=True)

        self.assertTrue(variable_indices_info.success)
        self.assertEqual(variable_indices_info.data, [x for x in range(20)])

    def test_10_valid_spec(self):
        """(10) Run DP Mean valid spec"""
        msgt(self.test_10_valid_spec.__doc__)

        spec_props = {'variable': 'Subject',
                      'col_index': 0,
                      'statistic': astatic.DP_HISTOGRAM,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      # 'accuracy': None,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': 5,
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'categories': ['"ac"', '"kj"', '"ys"', '"bh1"', '"bh2"', '"jm"', '"mh"', '"cw"',
                                                       '"jp"', '"rh"', '"aq"', '"ph"', '"le"', '"mn"', '"ls2"', '"no"',
                                                       '"af"'],
                                        'type': 'Float', },
                      }

        dp_hist = DPHistogramSpec(spec_props)
        self.assertTrue(dp_hist.is_chain_valid())

        for epsilon_val in [0.1, .25, .65, .431, 1.0]:
            print(f'> Valid epsilon val: {epsilon_val}')
            spec_props['epsilon'] = epsilon_val
            dp_hist = DPHistogramSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        print('   --------')
        for ci_val in [x[0] for x in astatic.CI_CHOICES]:
            print(f'> Valid ci val: {ci_val}')
            spec_props['ci'] = ci_val
            dp_hist = DPHistogramSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        print('   --------')
        for good_ds in [1, 2, 10, 100, 56 ** 3, ]:
            spec_props['dataset_size'] = good_ds
            dp_hist = DPHistogramSpec(spec_props)
            print(f'> Valid dataset_size: {good_ds}')
            self.assertTrue(dp_hist.is_chain_valid())

    def test_30_bad_ci(self):
        """(30) Bad ci vals"""
        msgt(self.test_30_bad_ci.__doc__)

        spec_props = {'variable': 'Subject',
                      'col_index': 0,
                      'statistic': astatic.DP_HISTOGRAM,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': 5,
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'categories': ['"ac"', '"kj"', '"ys"', '"bh1"', '"bh2"', '"jm"', '"mh"', '"cw"',
                                                       '"jp"', '"rh"', '"aq"', '"ph"', '"le"', '"mn"', '"ls2"', '"no"',
                                                       '"af"'],
                                        'type': 'Float', },
                      }

        def float_range(start, stop, step):
            while start < stop:
                yield float(start)
                start += decimal.Decimal(step)

        for ci_val in list(float_range(-1, 3, '0.1')) + ['alphabet', 'soup']:
            # print(f'> Invalid ci val: {ci_val}')
            spec_props['ci'] = ci_val
            dp_hist = DPHistogramSpec(spec_props)
            # print(dp_hist.is_chain_valid())
            self.assertTrue(dp_hist.is_chain_valid())

    def test_40_test_impute(self):
        """(40) Test impute validation"""
        msgt(self.test_40_test_impute.__doc__)

        spec_props = {'variable': 'Subject',
                      'col_index': 0,
                      'statistic': astatic.DP_HISTOGRAM,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': 5,
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'categories': ['"ac"', '"kj"', '"ys"', '"bh1"', '"bh2"', '"jm"', '"mh"', '"cw"',
                                                       '"jp"', '"rh"', '"aq"', '"ph"', '"le"', '"mn"', '"ls2"', '"no"',
                                                       '"af"'],
                                        'type': 'Float', },
                      }

        dp_hist = DPHistogramSpec(spec_props)
        if not dp_hist.is_chain_valid():
            print(dp_hist.get_error_messages())
        self.assertTrue(dp_hist.is_chain_valid())

        bad_impute_info = [(-10, astatic.ERR_IMPUTE_PHRASE_MIN)]

        for bad_impute, stat_err_msg in bad_impute_info:
            print(f'> bad impute: {bad_impute}')
            new_props = spec_props.copy()
            new_props['fixed_value'] = bad_impute
            dp_hist2 = DPHistogramSpec(new_props)

            self.assertFalse(dp_hist2.is_chain_valid())
            err_dict = dp_hist2.get_error_msg_dict()
            print(f"  - {err_dict['message']}")
            self.assertTrue(err_dict['message'].find(stat_err_msg) > -1)

        good_impute_info = [-8, 5, '-8', '5', -7, 0, '0']

        for good_impute in good_impute_info:
            print(f'> good impute: {good_impute}')
            new_props = spec_props.copy()
            new_props['fixed_value'] = good_impute
            dp_hist = DPHistogramSpec(new_props)
            self.assertTrue(dp_hist.is_chain_valid())

    # @skip
    def test_100_run_dphist_calculation(self):
        """(100) Run DP mean calculation"""
        msgt(self.test_100_run_dphist_calculation.__doc__)

        spec_props = {'variable': 'Subject',
                      'col_index': 0,
                      'statistic': astatic.DP_HISTOGRAM,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      # 'accuracy': None,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': 5,
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'categories': ['"ac"', '"kj"', '"ys"', '"bh1"', '"bh2"', '"jm"', '"mh"',
                                                       '"cw"', '"jp"', '"rh"', '"aq"', '"ph"', '"le"', '"mn"',
                                                       '"ls2"', '"no"', '"af"'],
                                        'type': 'Integer', },
                      }

        dp_hist = DPHistogramSpec(spec_props)
        print(dp_hist.has_error(), dp_hist.error_messages)
        if dp_hist.has_error():
            print(dp_hist.get_error_messages())
        self.assertTrue(dp_hist.is_chain_valid())
        # print('\nUI info:', json.dumps(dp_hist.get_success_msg_dict()))

        # ------------------------------------------------------
        # Run the actual mean
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
        dp_hist.run_chain(col_indexes, file_obj, sep_char="\t")

    def test_105_run_dphist_calculation_categorical(self):
        """(105) Run DP mean calculation with labels"""
        msgt(self.test_105_run_dphist_calculation_categorical.__doc__)

        spec_props = {
            'variable': 'Subject',
            'col_index': 0,
            'statistic': astatic.DP_HISTOGRAM,
            'dataset_size': 183,
            'epsilon': 1.0,
            'delta': 0.0,
            'ci': astatic.CI_95,
            'fixed_value': 1,
            'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
            'variable_info': {
                'min': 0,
                'max': 1E5,
                'categories': ['"ac"', '"kj"', '"ys"', '"bh1"', '"bh2"', '"jm"', '"mh"', '"cw"', '"jp"', '"rh"', '"aq"',
                               '"ph"', '"le"', '"mn"', '"ls2"', '"no"', '"af"'],
                'type': 'Categorical'
            }
        }

        dp_hist = DPHistogramSpec(spec_props)
        print(f"DPHistogramSpec valid? {dp_hist.has_error()}. get_error_msg_dict: {dp_hist.get_error_msg_dict()}")
        if dp_hist.has_error():
            print(f"get_error_messages(): {dp_hist.get_error_messages()}")
        self.assertTrue(dp_hist.is_chain_valid())
        # print('\nUI info:', json.dumps(dp_hist.get_success_msg_dict()))

        # ------------------------------------------------------
        # Run the actual mean
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
        dp_hist.run_chain(col_indexes, file_obj, sep_char="\t")
        print(dp_hist.statistic)

