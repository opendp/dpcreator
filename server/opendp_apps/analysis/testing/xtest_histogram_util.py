import decimal
from os.path import abspath, dirname, isfile, join

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_histogram_int_one_per_value_spec import DPHistogramIntOnePerValueSpec
from opendp_apps.analysis.tools.histogram_util import HistogramUtil
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.profiler import static_vals as pstatic


class HistogramUtilTest(StatSpecTestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):

        super().setUp()

        """Reusable properties for testing basic 'StatSpec' functionality"""

        self.spec_props = {
            'variable': 'optimism',
            'col_index': 5,
            'statistic': astatic.DP_HISTOGRAM,
            'histogram_bin_type': astatic.HIST_BIN_TYPE_EQUAL_RANGES,
            'histogram_number_of_bins': 4,
            'histogram_bin_edges': None,
            'dataset_size': 7000,
            'epsilon': 1,
            'delta': 0.0,
            'cl': astatic.CL_95,
            'fixed_value': 25,
            'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
            'variable_info': {
                'min': 6,
                'max': 30,
                'type': pstatic.VAR_TYPE_INTEGER
            }
        }

        self.dp_hist = DPHistogramIntOnePerValueSpec(self.spec_props)

        if self.dp_hist.has_error():
            print(self.dp_hist.get_error_messages())
        self.assertFalse(self.dp_hist.has_error())
        self.assertTrue(self.dp_hist.is_chain_valid())

    def test_010_test_int_valid_bins(self):
        """(10) Check DPHistogramIntOnePerValueSpec with valid bins"""
        msgt(self.test_010_test_int_valid_bins.__doc__)

        dp_hist = DPHistogramIntOnePerValueSpec(self.spec_props)

        hist_util = HistogramUtil(dp_hist)

        self.assertFalse(hist_util.has_error())

        self.assertTrue(hist_util.use_bin_edges())
        self.assertEqual(hist_util.get_bin_edges(), [6, 12, 18, 24, 31])
        if hist_util.has_error():
            print('errors', hist_util.get_err_msg())
        else:
            if hist_util.use_bin_edges():
                print('hist_util edges', hist_util.get_bin_edges())
            else:
                print('hist_util categories', hist_util.get_categories())
