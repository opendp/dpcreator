from os.path import abspath, dirname, join
import json
import uuid

from unittest import skip
from django.test import TestCase
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis.tools.dp_mean_spec import DPMeanSpec

from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.analysis import static_vals as astatic

from opendp_apps.model_helpers.msg_util import msgt


class StatSpecTest(TestCase):

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
        print('  - Is valid?', dp_mean.is_valid())
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

        print('(2) dp_mean.is_valid()', dp_mean.is_valid())
        print('(2a) dp_mean.is_valid()', dp_mean.is_valid())
        #print(dp_mean.get_error_messages())
        #self.assertTrue(dp_mean.is_valid())

        #print('(3) accuracy', dp_mean.get_accuracy())

        if dp_mean.has_error():
            print(dp_mean.get_error_messages())

        dp_mean.create_statistic()
        #self.assertTrue(dp_mean.has_error())
        #print('dp_mean.is_valid()', dp_mean.is_valid())
        #print('dp_mean.has_error()', dp_mean.has_error())
        #print(dp_mean.get_error_messages())


