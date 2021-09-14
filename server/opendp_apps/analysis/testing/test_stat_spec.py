from os.path import abspath, dirname, join
import json
import uuid

#from unittest import skip
from django.test import TestCase
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis.tools.dp_mean_spec import DPMeanInfo

from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.analysis import static_vals as astatic

from opendp_apps.model_helpers.msg_util import msgt


class StatSpecTest(TestCase):

    def test_10_dp_mean(self):
        """(10) Test DP Mean Spec"""
        msgt(self.test_10_dp_mean.__doc__)

        spec_props = dict(var_name="hours_sleep",
                          col_index=3,
                          variable_info=dict(min=0, max=24, type=pstatic.VAR_TYPE_FLOAT),
                          statistic=astatic.DP_MEAN,
                          impute_constant=5,
                          dataset_size=365,
                          epsilon=0.5,
                          ci=astatic.CI_95)

        dp_mean = DPMeanInfo(spec_props)
        print('(1) Setup dp_mean.has_error()', dp_mean.has_error())
        if dp_mean.has_error():
            print(dp_mean.get_error_messages())
        self.assertFalse(dp_mean.has_error())

        print('(2) dp_mean.is_valid()', dp_mean.is_valid())
        if dp_mean.has_error():
            print(dp_mean.get_error_messages())
        #self.assertTrue(dp_mean.has_error())
        #print('dp_mean.is_valid()', dp_mean.is_valid())
        #print('dp_mean.has_error()', dp_mean.has_error())
        #print(dp_mean.get_error_messages())