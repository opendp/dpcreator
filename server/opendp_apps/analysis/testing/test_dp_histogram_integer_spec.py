import decimal
from os.path import abspath, dirname, isfile, join

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_histogram_int_one_per_value_spec import DPHistogramIntOnePerValueSpec
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.profiler import static_vals as pstatic


class HistogramIntegerStatSpecTest(StatSpecTestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):

        super().setUp()

        """Reusable properties for testing basic 'StatSpec' functionality"""

        self.spec_props = {
            'variable': 'optimism',
            'col_index': 5,
            'statistic': astatic.DP_HISTOGRAM,
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

    def test_001_valid_noise_mechanism(self):
        """(1) Check for the correct noise_mechanism"""
        msgt(self.test_001_valid_noise_mechanism.__doc__)
        dp_hist_int = DPHistogramIntOnePerValueSpec({})
        self.assertEqual(dp_hist_int.noise_mechanism, astatic.NOISE_GEOMETRIC_MECHANISM)

    def test_005_get_variable_order(self):
        """(5) Test get variable order"""
        msgt(self.test_005_get_variable_order.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_indices_info = analysis_plan.dataset.get_variable_order(as_indices=True)

        self.assertTrue(variable_indices_info.success)
        self.assertEqual(variable_indices_info.data, [x for x in range(20)])

    def test_010_valid_spec(self):
        """(10) Run DP Mean valid spec"""
        msgt(self.test_010_valid_spec.__doc__)

        spec_props = self.spec_props.copy()

        for epsilon_val in [0.1, .25, .65, .431, 1.0]:
            print(f'> Valid epsilon val: {epsilon_val}')
            spec_props['epsilon'] = epsilon_val
            dp_hist = DPHistogramIntOnePerValueSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        print('   --------')
        for cl_val in [x[0] for x in astatic.CL_CHOICES]:
            print(f'> Valid cl val: {cl_val}')
            spec_props['cl'] = cl_val
            dp_hist = DPHistogramIntOnePerValueSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        print('   --------')
        for good_ds in [1, 2, 10, 100, 56 ** 3, ]:
            spec_props['dataset_size'] = good_ds
            dp_hist = DPHistogramIntOnePerValueSpec(spec_props)
            print(f'> Valid dataset_size: {good_ds}')
            self.assertTrue(dp_hist.is_chain_valid())

    def test_030_bad_confidence_levels(self):
        """(30) Bad confidence level values"""
        msgt(self.test_030_bad_confidence_levels.__doc__)

        spec_props = self.spec_props

        def float_range(start, stop, step):
            while start < stop:
                yield float(start)
                start += decimal.Decimal(step)

        for cl_val in list(float_range(-1, 0, '0.1')) + ['alphabet', 'soup']:
            # print(f'> Invalid ci val: {ci_val}')
            spec_props['cl'] = cl_val
            dp_hist = DPHistogramIntOnePerValueSpec(spec_props)
            # print(dp_hist.is_chain_valid())
            valid = dp_hist.is_chain_valid()
            print(dp_hist.error_messages)
            print(cl_val)
            self.assertFalse(valid)

    def test_040_test_impute(self):
        """(40) Test impute validation"""
        msgt(self.test_040_test_impute.__doc__)

        new_props = self.spec_props.copy()

        bad_impute_info = [(-10, astatic.ERR_IMPUTE_PHRASE_MIN)]

        for bad_impute, stat_err_msg in bad_impute_info:
            print(f'> bad impute: {bad_impute}')
            new_props['fixed_value'] = bad_impute
            dp_hist2 = DPHistogramIntOnePerValueSpec(new_props)

            self.assertFalse(dp_hist2.is_chain_valid())
            err_dict = dp_hist2.get_error_msg_dict()
            print(f"  - {err_dict['message']}")
            self.assertTrue(err_dict['message'].find(stat_err_msg) > -1)

    def test_120_run_dphist_calculation_integer(self):
        """(120) Run DP histogram calculation with integer values"""
        msgt(self.test_120_run_dphist_calculation_integer.__doc__)

        spec_props = {
            'variable': 'Trial',
            'col_index': 4,
            'statistic': astatic.DP_HISTOGRAM,
            'dataset_size': 183,
            'epsilon': 1,
            'delta': 0.0,
            'cl': astatic.CL_95,
            'fixed_value': "3",
            'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
            'variable_info': {
                'min': 0,
                'max': 7,
                'type': pstatic.VAR_TYPE_INTEGER
            }
        }

        dp_hist = DPHistogramIntOnePerValueSpec(spec_props)
        # if not dp_hist.is_chain_valid(): print(f"get_error_messages(): {dp_hist.get_error_messages()}")
        self.assertTrue(dp_hist.is_chain_valid())

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

        release_dict = dp_hist.get_release_dict()
        # import json; print(json.dumps(release_dict, indent=4))

        # expecting 9 categories. 8 + uncategorized
        self.assertEqual(9, len(release_dict['result']['value']['categories']))

        # check that category_value_pairs are included--and that there are 9 of them
        self.assertEqual(9, len(release_dict['result']['value']['category_value_pairs']))

        # Note: much wider than actual range
        self.assertTrue(release_dict['accuracy']['value'] < 6)
        self.assertTrue(release_dict['accuracy']['value'] > 4)

        # Check that the fixed_value is in the list of categories
        #
        fixed_value = release_dict['missing_value_handling']['fixed_value']
        categories = release_dict['result']['value']['categories']
        self.assertTrue(fixed_value in categories)

    def test_130_run_dphist_calculation_integer(self):
        """(130) Run DP histogram calculation with integer values"""
        msgt(self.test_130_run_dphist_calculation_integer.__doc__)

        dp_hist = DPHistogramIntOnePerValueSpec(self.spec_props)
        self.assertTrue(dp_hist.is_chain_valid())
        # print('\nUI info:', json.dumps(dp_hist.get_success_msg_dict()))

        # ------------------------------------------------------
        # Run the actual mean
        # ------------------------------------------------------
        # Column indexes - We know this data has 10 columns
        col_indexes = [idx for idx in range(0, 10)]

        # File object
        #
        teacher_survey_filepath = join(TEST_DATA_DIR, 'teacher_survey', 'teacher_survey.csv')
        self.assertTrue(isfile(teacher_survey_filepath))

        file_obj = open(teacher_survey_filepath, 'r')

        # Call run_chain
        #
        dp_hist.run_chain(col_indexes, file_obj, sep_char=",")

        release_dict = dp_hist.get_release_dict()
        # import json; print(json.dumps(release_dict, indent=4))

        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)

        # expecting 26 categories. 25 + uncategorized
        self.assertEqual(26, len(release_dict['result']['value']['categories']))

        # check that category_value_pairs are included--and that there are 9 of them
        self.assertEqual(26, len(release_dict['result']['value']['category_value_pairs']))

        # Check that the fixed_value is in the list of categories
        #
        fixed_value = release_dict['missing_value_handling']['fixed_value']
        categories = release_dict['result']['value']['categories']
        self.assertTrue(fixed_value in categories)