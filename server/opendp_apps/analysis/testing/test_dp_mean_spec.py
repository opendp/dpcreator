from os.path import abspath, dirname, isdir, isfile, join
CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from unittest import skip

import json
import decimal

from django.contrib.auth import get_user_model
# from django.core.files import File
from django.test.testcases import TestCase

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.dataset.models import DataSetInfo

from unittest import skip
from opendp_apps.analysis.tools.dp_mean_spec import DPMeanSpec

from opendp_apps.analysis import static_vals as astatic

from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils.extra_validators import *




class StatSpecTest(TestCase):

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
    def test_10_debug_mean(self):
        """(10) Test DP Mean Spec"""
        msgt(self.test_10_debug_mean.__doc__)

        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': astatic.DP_MEAN,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      #'accuracy': None,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '0',
                      'variable_info': {'min': 0,
                                        'max': 100,
                                        'type': 'Float',},
                      }

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
                      'ci': astatic.CI_95,
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
        for ci_val in [x[0] for x in astatic.CI_CHOICES]:
            print(f'> Valid ci val: {ci_val}')
            spec_props['ci'] = ci_val
            dp_mean = DPMeanSpec(spec_props)
            self.assertTrue(dp_mean.is_chain_valid())

        print('   --------')
        for good_ds in [1, 2, 10, 100, 56**3,]:
            spec_props['dataset_size'] = good_ds
            dp_mean = DPMeanSpec(spec_props)
            print(f'> Valid dataset_size: {good_ds}')
            self.assertTrue(dp_mean.is_chain_valid())

    @skip
    def test_20_bad_epsilon(self):
        """(20) Bad epsilon"""
        msgt(self.test_20_bad_epsilon.__doc__)

        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': astatic.DP_MEAN,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '5',
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'type': 'Float', },
                      }


        for epsilon_val in [1.01, -0.01, 10, 'a', 'carrot', 'cake']:
            print(f'> Bad epsilon val: {epsilon_val}')
            spec_props['epsilon'] = epsilon_val
            dp_mean = DPMeanSpec(spec_props)

            self.assertFalse(dp_mean.is_chain_valid())
            err_info = dp_mean.get_error_msg_dict()
            self.assertTrue(err_info['valid'] == False)
            print(err_info['message'])
            self.assertTrue(err_info['message'].find(VALIDATE_MSG_EPSILON) > -1)

        print('     ---')

        spec_props['epsilon'] = 1
        for bad_ds in [-1, 0, 1.0, .03, 'brick', 'cookie']:
            print(f'> Bad dataset_size: {bad_ds}')
            spec_props['dataset_size'] = bad_ds
            dp_mean = DPMeanSpec(spec_props)
            self.assertFalse(dp_mean.is_chain_valid())

    def test_30_bad_ci(self):
        """(30) Bad ci vals"""
        msgt(self.test_30_bad_ci.__doc__)

        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': astatic.DP_MEAN,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '5',
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'type': 'Float', },
                      }
        def float_range(start, stop, step):
            while start < stop:
                yield float(start)
                start += decimal.Decimal(step)

        for ci_val in list(float_range(-1, 3, '0.08')):
            #print(f'> Invalid ci val: {ci_val}')
            spec_props['ci'] = ci_val
            dp_mean = DPMeanSpec(spec_props)
            #print(dp_mean.is_chain_valid())
            self.assertFalse(dp_mean.is_chain_valid())
            self.assertTrue(dp_mean.get_single_err_msg().find(VALIDATE_MSG_NOT_VALID_CI) > -1)

        for ci_val in ['alphabet', 'soup', 'c']:
            #print(f'> Invalid ci val: {ci_val}')
            spec_props['ci'] = ci_val
            dp_mean = DPMeanSpec(spec_props)
            #print(dp_mean.is_chain_valid())
            self.assertFalse(dp_mean.is_chain_valid())
            self.assertTrue(dp_mean.get_single_err_msg().find('Failed to convert "ci" to a float') > -1)



    def test_40_test_impute(self):
        """(40) Test impute validation"""
        msgt(self.test_40_test_impute.__doc__)

        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': astatic.DP_MEAN,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '5.0',
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'type': 'Float', },
                      }

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


        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': astatic.DP_MEAN,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': astatic.CI_95,
                      #'accuracy': None,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '5',
                      'variable_info': {'min': -8,
                                        'max': 5,
                                        'type': 'Float',},
                      }

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



        print('Actual mean: -0.9503854412185792')
        '''
           Some actual stats:
               "invalidCount": 0,
               "validCount": 183,
               "uniqueCount": 183,
               "median": -0.851190845,
               "mean": -0.9503854412185792,
               "max": 4.846733074,
               "min": -7.953123756,
               "mode": [
                   -0.453860599,
                   2.120359194,
                   3.045188197,
                   2.803143496,
                   -0.641054302
               ],
        '''

"""
# from ./dpcreator/server directory

import os
from raven_preprocess.preprocess_runner import PreprocessRunner

fnames =  ['PUMS5extract1000.csv', 'PUMS5extract10000.csv', 
           'Fatigue_data.tab', 'gking-crisis.tab',
           'teacher_climate_survey_lwd.csv', 'fearonLaitin.csv']
for fname in fnames:
    fpath = join(os.getcwd(), 'test_data', fname)
    run_info = PreprocessRunner.load_from_file(fpath)
    if not run_info.success:
        print(run_info.err_msg)
    else:
        runner = run_info.result_obj
        fname_base = fname.split('.')[0]
        out_path = join(os.getcwd(), 'test_data', 
                        'non_dp_debug_info', f'info_{fname_base}.json')
        open(out_path, 'w').write(runner.get_final_json(indent=4))
        print('file written: ', out_path)

    # show the JSON (string)
    print(runner.get_final_json(indent=4))
    
    metadata = runner.get_final_dict()
    print(metadata['variables']['EyeHeight']
"""