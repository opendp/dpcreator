import json
import decimal

from os.path import abspath, dirname, isfile, join
from unittest import skip

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
# from opendp_apps.analysis.tools.dp_histogram_spec import DPHistogramSpec
from opendp_apps.analysis.tools.dp_histogram_categorical_spec import DPHistogramCategoricalSpec
from opendp_apps.analysis.tools.dp_histogram_integer_spec import DPHistogramIntegerSpec
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils.extra_validators import *
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.profiler import static_vals as pstatic


class HistogramStatSpecTest(StatSpecTestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):

        super().setUp()

        """Reusable properties for testing basic 'StatSpec' functionality"""

        self.spec_props = {'variable': 'Subject',
                      'col_index': 0,
                      'statistic': astatic.DP_HISTOGRAM,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'cl': astatic.CL_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': 'ac',
                      'variable_info': {'categories': ['ac', 'kj', 'ys', 'bh1', 'bh2', 'jm', 'mh', 'cw',
                                                       'jp', 'rh', 'aq', 'ph', 'le', 'mn', 'ls2', 'no',
                                                       'af'],
                                        'type': pstatic.VAR_TYPE_CATEGORICAL},
                      }

        self.dp_hist = DPHistogramCategoricalSpec(self.spec_props)

        if self.dp_hist.has_error():
            print(self.dp_hist.get_error_messages())
        self.assertFalse(self.dp_hist.has_error())
        self.assertTrue(self.dp_hist.is_chain_valid())



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

        spec_props = self.spec_props.copy()

        for epsilon_val in [0.1, .25, .65, .431, 1.0]:
            print(f'> Valid epsilon val: {epsilon_val}')
            spec_props['epsilon'] = epsilon_val
            dp_hist = DPHistogramCategoricalSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        print('   --------')
        for cl_val in [x[0] for x in astatic.CL_CHOICES]:
            print(f'> Valid cl val: {cl_val}')
            spec_props['cl'] = cl_val
            dp_hist = DPHistogramCategoricalSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        print('   --------')
        for good_ds in [1, 2, 10, 100, 56 ** 3, ]:
            spec_props['dataset_size'] = good_ds
            dp_hist = DPHistogramCategoricalSpec(spec_props)
            print(f'> Valid dataset_size: {good_ds}')
            self.assertTrue(dp_hist.is_chain_valid())

    def test_30_bad_confidence_levels(self):
        """(30) Bad confidence level values"""
        msgt(self.test_30_bad_confidence_levels.__doc__)

        spec_props = self.spec_props

        def float_range(start, stop, step):
            while start < stop:
                yield float(start)
                start += decimal.Decimal(step)

        for cl_val in list(float_range(-1, 3, '0.1')) + ['alphabet', 'soup']:
            # print(f'> Invalid ci val: {ci_val}')
            spec_props['cl'] = cl_val
            dp_hist = DPHistogramCategoricalSpec(spec_props)
            # print(dp_hist.is_chain_valid())
            self.assertTrue(dp_hist.is_chain_valid())

    @skip
    # Not clear that this test should pass anymore, since min/max was referring to
    # numerical values and this is categorical
    def test_40_test_impute(self):
        """(40) Test impute validation"""
        msgt(self.test_40_test_impute.__doc__)

        spec_props = self.spec_props.copy()

        dp_hist = DPHistogramCategoricalSpec(spec_props)
        if not dp_hist.is_chain_valid():
            print(dp_hist.get_error_messages())
        self.assertTrue(dp_hist.is_chain_valid())

        bad_impute_info = [(-10, astatic.ERR_IMPUTE_PHRASE_MIN)]

        for bad_impute, stat_err_msg in bad_impute_info:
            print(f'> bad impute: {bad_impute}')
            new_props = spec_props.copy()
            new_props['fixed_value'] = bad_impute
            dp_hist2 = DPHistogramIntegerSpec(new_props)

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

    def test_100_run_dphist_calculation_categorical(self):
        """(100) Run DP histogram calculation"""
        msgt(self.test_100_run_dphist_calculation_categorical.__doc__)

        dp_hist = self.dp_hist
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
        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)


    def test_110_run_dphist_calculation_categorical2(self):
        """(110) Run DP 2nd categorical calculation, with only 2 categories"""
        msgt(self.test_110_run_dphist_calculation_categorical2.__doc__)

        spec_props = {
            'variable': 'Language',
            'col_index': 1,
            'statistic': astatic.DP_HISTOGRAM,
            'dataset_size': 183,
            'epsilon': 1.0,
            'delta': 0.0,
            'cl': astatic.CL_95,
            'fixed_value': 'EN',
            'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
            'variable_info': {
                'categories': ['EN', 'DA'],
                'type': 'Categorical'
            }
        }

        dp_hist = DPHistogramCategoricalSpec(spec_props)
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
        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)


    def test_120_run_dphist_calculation_integer(self):
        """(120) Run DP histogram calculation with integer values"""
        msgt(self.test_120_run_dphist_calculation_integer.__doc__)

        spec_props = {
            'variable': 'Trial',
            'col_index': 4,
            'statistic': astatic.DP_HISTOGRAM,
            'dataset_size': 183,
            'epsilon': 1.0,
            'delta': 0.0,
            'cl': astatic.CL_95,
            'fixed_value': 3,
            'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
            'variable_info': {
                'min': 0,
                'max': 7,
                'type': 'Integer'
            }
        }

        dp_hist = DPHistogramIntegerSpec(spec_props)
        print(f"DPHistogramIntegerSpecSpec valid? {dp_hist.has_error()}. get_error_msg_dict: {dp_hist.get_error_msg_dict()}")
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

        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)
