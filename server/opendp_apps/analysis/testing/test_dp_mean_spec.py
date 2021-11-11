import json
import decimal

from os.path import abspath, dirname, isfile, join
from unittest import skip

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_mean_spec import DPMeanSpec
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils.extra_validators import *


class DPMeanStatSpecTest(StatSpecTestCase):

    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):

        super().setUp()

        self.spec_props = {'variable': 'EyeHeight',
                          'col_index': 19,
                          'statistic': astatic.DP_MEAN,
                          'dataset_size': 183,
                          'epsilon': 1.0,
                          'delta': 0.0,
                          'cl': astatic.CL_95,
                          'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                          'fixed_value': '5',
                          'variable_info': {'min': -8,
                                            'max': 5,
                                            'type': 'Float', },
                        }

        self.spec_props_income = {'variable': 'income',
                                  'col_index': 6,
                                  'statistic': astatic.DP_MEAN,
                                  'dataset_size': 10000,
                                  'epsilon': 0.6,
                                  'delta': 0.0,
                                  'cl': astatic.CL_99,
                                  'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                                  'fixed_value': '31000',
                                  'variable_info': {'min': 0,
                                                    'max': 650000,
                                                    'type': 'Float',},
                                  }

    #@skip
    def test_10_debug_mean(self):
        """(10) Test DP Mean Spec"""
        msgt(self.test_10_debug_mean.__doc__)

        spec_props = self.spec_props

        dp_mean = DPMeanSpec(spec_props)
        print('(1) Run initial check, before using the OpenDp library')
        print('  - Error found?', dp_mean.has_error())
        if dp_mean.has_error():
            print('\n-- Errors --')
            print(dp_mean.get_error_messages())
            print('\nUI info:', json.dumps(dp_mean.get_error_msg_dict()))
            return

        print('(2) Use the OpenDP library to check validity')
        print('  - Is valid?', dp_mean.is_chain_valid())
        if dp_mean.has_error():
            print('\n-- Errors --')
            print(dp_mean.get_error_messages())
            print('\nUI info:', json.dumps(dp_mean.get_error_msg_dict()))
        else:
            print('\n-- Looks good! --')
            print('\nUI info:', json.dumps(dp_mean.get_success_msg_dict()))


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

        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': astatic.DP_MEAN,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'cl': astatic.CL_95,
                      #'accuracy': None,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '5',
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'type': 'Float',},
                      }

        dp_mean = DPMeanSpec(spec_props)
        self.assertTrue(dp_mean.is_chain_valid())

        for epsilon_val in [0.1, .25, .65, .431, 1.0]:
            print(f'> Valid epsilon val: {epsilon_val}')
            spec_props['epsilon'] = epsilon_val
            dp_mean = DPMeanSpec(spec_props)
            self.assertTrue(dp_mean.is_chain_valid())

        print('   --------')
        for cl_val in [x[0] for x in astatic.CL_CHOICES]:
            print(f'> Valid CL val: {cl_val}')
            spec_props['cl'] = cl_val
            dp_mean = DPMeanSpec(spec_props)
            self.assertTrue(dp_mean.is_chain_valid())

        print('   --------')
        for good_ds in [1, 2, 10, 100, 56**3,]:
            spec_props['dataset_size'] = good_ds
            dp_mean = DPMeanSpec(spec_props)
            print(f'> Valid dataset_size: {good_ds}')
            self.assertTrue(dp_mean.is_chain_valid())

    # @skip
    def test_20_bad_epsilon(self):
        """(20) Bad epsilon"""
        msgt(self.test_20_bad_epsilon.__doc__)

        spec_props = self.spec_props


        for epsilon_val in [1.01, -0.01, 10]:
            print(f'> Bad epsilon val: {epsilon_val}')
            spec_props['epsilon'] = epsilon_val
            dp_mean = DPMeanSpec(spec_props)

            self.assertFalse(dp_mean.is_chain_valid())
            err_info = dp_mean.get_error_msg_dict()
            self.assertTrue(err_info['valid'] == False)
            print(err_info['message'])
            self.assertTrue(err_info['message'].find(VALIDATE_MSG_EPSILON) > -1)

        for epsilon_val in ['a', 'carrot', 'cake']:
            print(f'> Bad epsilon val: {epsilon_val}')
            spec_props['epsilon'] = epsilon_val
            dp_mean = DPMeanSpec(spec_props)

            self.assertFalse(dp_mean.is_chain_valid())
            err_info = dp_mean.get_error_msg_dict()
            self.assertTrue(err_info['valid'] == False)
            print(err_info['message'])
            self.assertTrue(err_info['message'].find('Failed to convert') > -1)


        spec_props['epsilon'] = 1
        for bad_ds in [-1, 0, 1.0, .03, 'brick', 'cookie']:
            print(f'> Bad dataset_size: {bad_ds}')
            spec_props['dataset_size'] = bad_ds
            dp_mean = DPMeanSpec(spec_props)
            self.assertFalse(dp_mean.is_chain_valid())

    def test_30_bad_confidence_levels(self):
        """(30) Bad confidence level vals"""
        msgt(self.test_30_bad_confidence_levels.__doc__)

        spec_props = self.spec_props

        def float_range(start, stop, step):
            while start < stop:
                yield float(start)
                start += decimal.Decimal(step)

        for cl_val in list(float_range(-1, 3, '0.08')):
            #print(f'> Invalid ci val: {ci_val}')
            spec_props['cl'] = cl_val
            dp_mean = DPMeanSpec(spec_props)
            #print(dp_mean.is_chain_valid())
            self.assertFalse(dp_mean.is_chain_valid())
            self.assertTrue(dp_mean.get_single_err_msg().find(VALIDATE_MSG_NOT_VALID_CL_VALUE) > -1)

        for cl_val in ['alphabet', 'soup', 'c']:
            #print(f'> Invalid ci val: {ci_val}')
            spec_props['cl'] = cl_val
            dp_mean = DPMeanSpec(spec_props)
            #print(dp_mean.is_chain_valid())
            self.assertFalse(dp_mean.is_chain_valid())
            self.assertTrue(dp_mean.get_single_err_msg().find('Failed to convert "cl" to a float') > -1)

    def test_35_check_confidence_level_alpha(self):
        """(35) Check accuracy with bad confidence level"""
        msgt(self.test_35_check_confidence_level_alpha.__doc__)

        # shouldn't happen, change cl after validity
        #
        spec_props_income = self.spec_props_income.copy()
        dp_mean = DPMeanSpec(spec_props_income)

        self.assertTrue(dp_mean.is_chain_valid())
        self.assertEqual(dp_mean.get_confidence_level_alpha(), astatic.CL_99_ALPHA)

        # Set CL to None -- shouldn't happen, would be caught in the __init__
        #
        dp_mean.cl = None
        cl_alpha = dp_mean.get_confidence_level_alpha()
        self.assertIsNone(cl_alpha)
        self.assertTrue(dp_mean.has_error())
        self.assertTrue(dp_mean.get_single_err_msg().startswith(astatic.ERR_MSG_CL_ALPHA_CL_NOT_SET))

        # Set CL to non numeric -- shouldn't happen, would be caught in the __init__
        #
        spec_props_income2 = self.spec_props_income.copy()
        dp_mean = DPMeanSpec(spec_props_income)
        self.assertTrue(dp_mean.is_chain_valid())
        dp_mean.cl = 'zebra'
        cl_alpha = dp_mean.get_confidence_level_alpha()
        self.assertIsNone(cl_alpha)

        self.assertTrue(dp_mean.has_error())
        self.assertTrue(dp_mean.get_single_err_msg().startswith(astatic.ERR_MSG_CL_ALPHA_CL_NOT_NUMERIC))

        # Set CL to 2.0 -- shouldn't happen, would be caught in the __init__
        #
        spec_props_income3 = self.spec_props_income.copy()
        dp_mean = DPMeanSpec(spec_props_income3)
        self.assertTrue(dp_mean.is_chain_valid())
        dp_mean.cl = 2.0
        cl_alpha = dp_mean.get_confidence_level_alpha()
        self.assertIsNone(cl_alpha)

        self.assertTrue(dp_mean.has_error())
        self.assertTrue(dp_mean.get_single_err_msg().startswith(astatic.ERR_MSG_CL_ALPHA_CL_LESS_THAN_0))

        # Set CL to -1 -- shouldn't happen, would be caught in the __init__
        #
        spec_props_income3 = self.spec_props_income.copy()
        dp_mean = DPMeanSpec(spec_props_income3)
        self.assertTrue(dp_mean.is_chain_valid())
        dp_mean.cl = -1.0
        cl_alpha = dp_mean.get_confidence_level_alpha()
        self.assertIsNone(cl_alpha)

        self.assertTrue(dp_mean.has_error())
        self.assertTrue(dp_mean.get_single_err_msg().startswith(astatic.ERR_MSG_CL_ALPHA_CL_GREATER_THAN_1))

    def test_40_test_impute(self):
        """(40) Test impute validation"""
        msgt(self.test_40_test_impute.__doc__)

        spec_props = self.spec_props


        dp_mean = DPMeanSpec(spec_props)
        self.assertTrue(dp_mean.is_chain_valid())


        bad_impute_info = [  (-10, astatic.ERR_IMPUTE_PHRASE_MIN)
                           , (45, astatic.ERR_IMPUTE_PHRASE_MAX)
                           , (5.2, astatic.ERR_IMPUTE_PHRASE_MAX)]

        for bad_impute, stat_err_msg in bad_impute_info:
            print(f'> bad impute: {bad_impute}')
            new_props = spec_props.copy()
            new_props['fixed_value'] = bad_impute
            dp_mean2 = DPMeanSpec(new_props)

            self.assertFalse(dp_mean2.is_chain_valid())
            err_dict = dp_mean2.get_error_msg_dict()
            print(f"  - {err_dict['message']}")
            self.assertTrue(err_dict['message'].find(stat_err_msg) > -1)


        good_impute_info = [-8, 5, '-8.0', '5.0000', -7, 0, '0.0']

        for good_impute in good_impute_info:
            print(f'> good impute: {good_impute}')
            new_props = spec_props.copy()
            new_props['fixed_value'] = good_impute
            dp_mean = DPMeanSpec(new_props)
            self.assertTrue(dp_mean.is_chain_valid())



    #@skip
    def test_100_run_dpmean_calculation(self):
        """(100) Run DP mean calculation"""
        msgt(self.test_100_run_dpmean_calculation.__doc__)

        spec_props = self.spec_props


        dp_mean = DPMeanSpec(spec_props)
        self.assertTrue(dp_mean.is_chain_valid())
        if dp_mean.has_error():
            print(dp_mean.get_error_messages())
            return
        #print('\nUI info:', json.dumps(dp_mean.get_success_msg_dict()))

        # ------------------------------------------------------
        # Run the actual mean
        # ------------------------------------------------------
        # Column indexes - We know this data has 20 columns
        col_indexes = [idx for idx in range(0,20)]

        # File object
        #
        eye_fatigue_filepath = join(TEST_DATA_DIR, 'Fatigue_data.tab')
        #print('eye_fatigue_filepath', eye_fatigue_filepath)
        self.assertTrue(isfile(eye_fatigue_filepath))

        file_obj = open(eye_fatigue_filepath, 'r')

        # Call run_chain
        #
        dp_mean.run_chain(col_indexes, file_obj, sep_char="\t")

        final_dict = dp_mean.get_release_dict()
        self.assertIn('description', final_dict)
        self.assertIn('text', final_dict['description'])
        self.assertIn('html', final_dict['description'])


        print('Actual mean: -0.9503854412185792')



    def test_110_run_dpmean_calculation(self):
        """(110) Run another DP mean calculation"""
        msgt(self.test_110_run_dpmean_calculation.__doc__)

        spec_props = self.spec_props_income

        dp_mean = DPMeanSpec(spec_props)
        print('Is this spec valid?', dp_mean.is_chain_valid())
        if dp_mean.has_error():
            print(dp_mean.get_error_messages())
            print(dp_mean.get_error_msg_dict())
            return
        self.assertTrue(dp_mean.is_chain_valid())

        # ------------------------------------------------------
        # Run the actual mean
        # ------------------------------------------------------
        # Column indexes - We know this data has 11 columns
        col_indexes = [idx for idx in range(0, 11)]

        # File object
        #
        pums_filepath = join(TEST_DATA_DIR, 'PUMS5extract10000.csv')
        self.assertTrue(isfile(pums_filepath))

        file_like_obj = open(pums_filepath, 'r')

        # Call run_chain
        #
        dp_mean.run_chain(col_indexes, file_like_obj)
        if dp_mean.has_error():
            print(dp_mean.get_error_messages())
            return

        final_dict = dp_mean.get_release_dict()

        json_str = json.dumps(final_dict, indent=4)
        print(json_str)

        print('-- actual vals --')
        print(('mean: 30,943.4566'
               '\nmin: -10,000.0'
               '\nmax: 713,000.0'))

        self.assertIn('description', final_dict)
        self.assertIn('text', final_dict['description'])
        self.assertIn('html', final_dict['description'])
