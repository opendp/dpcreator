from os.path import abspath, dirname, isdir, isfile, join
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
                      'statistic': 'mean',
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': 0.05,
                      #'accuracy': None,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'impute_constant': '0',
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


    @skip
    def test_15_dp_mean(self):
        """(15) Test DP Mean Spec"""
        msgt(self.test_15_dp_mean.__doc__)

        spec_props = dict(var_name="hours_sleep",
                          col_index=1,
                          variable_info=dict(min=1, max=16.0, type=pstatic.VAR_TYPE_FLOAT),
                          statistic=astatic.DP_MEAN,
                          missing_values_handling=astatic.MISSING_VAL_INSERT_FIXED,
                          impute_constant="8.0",
                          dataset_size=1000,
                          epsilon=1.0,
                          ci=astatic.CI_95)

        dp_mean = DPMeanSpec(spec_props)
        print('(1) Setup dp_mean.has_error()', dp_mean.has_error())
        if dp_mean.has_error():
            print(dp_mean.get_error_messages())
        self.assertFalse(dp_mean.has_error())

        # dp_mean.print_debug()

        print('(2) dp_mean.is_chain_valid()', dp_mean.is_chain_valid())
        print('(2a) dp_mean.is_chain_valid()', dp_mean.is_chain_valid())
        #print(dp_mean.get_error_messages())
        #self.assertTrue(dp_mean.is_chain_valid())

        #print('(3) accuracy', dp_mean.get_accuracy())

        if dp_mean.has_error():
            print(dp_mean.get_error_messages())

        dp_mean.create_statistic()
        #self.assertTrue(dp_mean.has_error())
        #print('dp_mean.is_chain_valid()', dp_mean.is_chain_valid())
        #print('dp_mean.has_error()', dp_mean.has_error())
        #print(dp_mean.get_error_messages())

    @skip
    def test_20_get_variable_order(self):
        """(20) Test get variable order"""
        msgt(self.test_20_get_variable_order.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_indices_info = analysis_plan.dataset.get_variable_order(as_indices=True)
        if variable_indices_info.success:
            print('variable_indices_info.data', variable_indices_info.data)
            variable_indices = variable_indices_info.data
        else:
            print('variable_indices_info.message', variable_indices_info.message)
            self.add_err_msg(variable_indices_info.message)


    def test_30_run_calculation(self):
        """(30) Run DP mean calculation"""
        msgt(self.test_30_run_calculation.__doc__)


        spec_props = {'variable': 'EyeHeight',
                      'col_index': 19,
                      'statistic': 'mean',
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'ci': 0.05,
                      #'accuracy': None,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'impute_constant': '5',
                      'variable_info': {'min': -8,
                                        'max': 5,
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

        return
        # ------------------------------------------------------
        # Run the actual mean
        # ------------------------------------------------------
        # Column indexes - We know this data has 20 columns
        col_indexes = [idx for idx in range(0,20)]

        # File object
        #
        eye_fatigue_filepath = join(TEST_DATA_DIR, 'Fatigue_data.tab')
        print('eye_fatigue_filepath', eye_fatigue_filepath)
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
from raven_preprocess.preprocess_runner import PreprocessRunner

run_info = PreprocessRunner.load_from_file(eye_fatigue_filepath)
if not run_info.success:
    print(run_info.err_msg)
else:
    runner = run_info.result_obj

    # show the JSON (string)
    print(runner.get_final_json(indent=4)
    
    metadata = runner.get_final_dict()
    print(metadata['variables']['EyeHeight']
"""