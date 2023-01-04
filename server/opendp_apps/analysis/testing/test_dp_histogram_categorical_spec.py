import decimal
from os.path import abspath, dirname, isfile, join

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_histogram_categorical_spec import DPHistogramCategoricalSpec
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.utils.extra_validators import VALIDATE_MSG_FIXED_VAL_NOT_IN_CATEGORIES
from opendp_apps.utils.variable_info_formatter import format_variable_info


class HistogramCategoricalStatSpecTest(StatSpecTestCase):
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

        # if self.dp_hist.has_error():
        #    print(self.dp_hist.get_error_messages())
        self.assertFalse(self.dp_hist.has_error())
        self.assertTrue(self.dp_hist.is_chain_valid())

    def test_001_valid_noise_mechanism(self):
        """(1) Check for the correct noise_mechanism"""
        msgt(self.test_001_valid_noise_mechanism.__doc__)

        self.assertEqual(self.dp_hist.noise_mechanism, astatic.NOISE_GEOMETRIC_MECHANISM)

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
            # print(f'> Valid epsilon val: {epsilon_val}')
            spec_props['epsilon'] = epsilon_val
            dp_hist = DPHistogramCategoricalSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        for cl_val in [x[0] for x in astatic.CL_CHOICES]:
            # print(f'> Valid cl val: {cl_val}')
            spec_props['cl'] = cl_val
            dp_hist = DPHistogramCategoricalSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        for good_ds in [1, 2, 10, 100, 56 ** 3, ]:
            spec_props['dataset_size'] = good_ds
            dp_hist = DPHistogramCategoricalSpec(spec_props)
            # print(f'> Valid dataset_size: {good_ds}')
            self.assertTrue(dp_hist.is_chain_valid())

    def test_030_bad_confidence_levels(self):
        """(30) Bad confidence level values"""
        msgt(self.test_030_bad_confidence_levels.__doc__)

        spec_props = self.spec_props

        def float_range(start, stop, step):
            while start < stop:
                yield float(start)
                start += decimal.Decimal(step)

        cl_vals = list(float_range(-1, 0, '0.1')) + ['alphabet', 'soup']
        for cl_val in cl_vals:
            # print(f'> Invalid ci val: {ci_val}')
            spec_props['cl'] = cl_val
            dp_hist = DPHistogramCategoricalSpec(spec_props)
            # print(dp_hist.is_chain_valid())
            valid = dp_hist.is_chain_valid()
            # print(dp_hist.error_messages)
            # print(cl_val)
            self.assertFalse(valid)

    def test_040_test_impute(self):
        """(40) Test impute validation"""
        msgt(self.test_040_test_impute.__doc__)

        spec_props = self.spec_props.copy()
        spec_props['fixed_value'] = 'unknown-one'

        dp_hist = DPHistogramCategoricalSpec(spec_props)
        #if not dp_hist.is_chain_valid():
        #    print(dp_hist.get_error_messages())
        self.assertTrue(dp_hist.is_chain_valid())

    def test_050_test_impute_unknown_fixed_value(self):
        """(50) Test impute validation, unknown fixed value"""
        msgt(self.test_050_test_impute_unknown_fixed_value.__doc__)

        spec_props = self.spec_props.copy()
        spec_props['fixed_value'] = 'not-a-known-category'

        dp_hist = DPHistogramCategoricalSpec(spec_props)
        #if not dp_hist.is_chain_valid(): print(dp_hist.get_error_messages())

        self.assertFalse(dp_hist.is_chain_valid())
        self.assertTrue(dp_hist.get_single_err_msg().find(VALIDATE_MSG_FIXED_VAL_NOT_IN_CATEGORIES) > -1)

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

        release_dict = dp_hist.get_release_dict()
        # import json; print(json.dumps(release_dict, indent=4))

        # Check that the fixed_value and list of categories are "unquoted"
        #
        fixed_value = release_dict['missing_value_handling']['fixed_value']
        self.assertEqual(fixed_value, DPHistogramCategoricalSpec._remove_double_quotes(fixed_value))

        categories = release_dict['result']['value']['categories']
        for cat_name in categories:
            self.assertEqual(cat_name, DPHistogramCategoricalSpec._remove_double_quotes(cat_name))

        # Check that the fixed_value is in the list of categories
        #
        self.assertTrue(fixed_value in categories)

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
                'type': pstatic.VAR_TYPE_CATEGORICAL
            }
        }

        dp_hist = DPHistogramCategoricalSpec(spec_props)
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

        release_dict = dp_hist.get_release_dict()
        # import json; print(json.dumps(release_dict, indent=4))

        # Check that the fixed_value and list of categories are "unquoted"
        #
        fixed_value = release_dict['missing_value_handling']['fixed_value']
        self.assertEqual(fixed_value, DPHistogramCategoricalSpec._remove_double_quotes(fixed_value))

        categories = release_dict['result']['value']['categories']
        for cat_name in categories:
            self.assertEqual(cat_name, DPHistogramCategoricalSpec._remove_double_quotes(cat_name))

        # Check that the fixed_value is in the list of categories
        #
        self.assertTrue(fixed_value in categories)

    def test_130_format_variable_info_categories(self):
        """(130) Test the formatting of variable info categories"""
        msgt(self.test_110_run_dphist_calculation_categorical2.__doc__)

        test_stats = {
            "trial": {
                "name": "Trial",
                "type": "Integer",
                "label": "",
                "sortOrder": 4
            },
            "session": {
                "name": "Session",
                "type": "Boolean",
                "label": "",
                "sortOrder": 2,
                "categories": []
            },
            "subject": {
                "name": "Subject",
                "type": "Categorical",
                "label": "Subject",
                "selected": True,
                "sortOrder": 0,
                "categories": [
                    "ac",
                    " kj",
                    " ys",
                    "zz",
                    "bh1  ",
                    " bh2    ",
                    " jm\n",
                    "\tmh",
                ]
            }
        }
        formatted_var_info = format_variable_info(test_stats)

        expected_cats = ['ac', 'kj', 'ys', 'zz', 'bh1', 'bh2', 'jm', 'mh']
        self.assertEqual(formatted_var_info['subject']['categories'], expected_cats)
        # print('var_info', formatted_var_info)

        self.assertEqual(format_variable_info(None), None)
        self.assertEqual(format_variable_info({}), {})
