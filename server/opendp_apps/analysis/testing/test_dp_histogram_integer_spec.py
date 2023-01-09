"""
docker-compose run server python manage.py test opendp_apps.analysis.testing.test_dp_histogram_integer_spec.HistogramIntegerStatSpecTest
"""
import decimal
import os
from os.path import abspath, dirname, isfile, join
import tempfile

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_histogram_int_one_per_value_spec import DPHistogramIntOnePerValueSpec
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.dp_reports.pdf_report_maker import PDFReportMaker
from opendp_apps.analysis.misc_formatters import get_timestamp_str

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')  # general test data
DP_REPORTS_TEST_DIR = join(dirname(dirname(CURRENT_DIR)), 'dp_reports', 'test_data')  # has sample release
DP_ANALYSIS_TEST_DIR = join(dirname(CURRENT_DIR), 'test_output')  # to write test PDFs (not saved)
if not isfile(DP_ANALYSIS_TEST_DIR):
    os.makedirs(DP_ANALYSIS_TEST_DIR, exist_ok=True)
    print('created: ', DP_ANALYSIS_TEST_DIR)


class HistogramIntegerStatSpecTest(StatSpecTestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):

        super().setUp()

        """Reusable properties for testing basic 'StatSpec' functionality"""

        self.spec_props_per_val = {
            'variable': 'optimism',
            'col_index': 5,
            'statistic': astatic.DP_HISTOGRAM,
            astatic.KEY_HIST_BIN_TYPE: astatic.HIST_BIN_TYPE_ONE_PER_VALUE,
            astatic.KEY_HIST_NUMBER_OF_BINS: None,
            astatic.KEY_HIST_BIN_EDGES: None,
            'dataset_size': 7000,
            'epsilon': 1,
            'delta': 0.0,
            'cl': astatic.CL_95,
            astatic.KEY_FIXED_VALUE: 25,
            astatic.KEY_MISSING_VALUES_HANDLING: astatic.MISSING_VAL_INSERT_FIXED,
            'variable_info': {
                'min': 6,
                'max': 30,
                'type': pstatic.VAR_TYPE_INTEGER
            }
        }

        self.dp_hist_per_val = DPHistogramIntOnePerValueSpec(self.spec_props_per_val)

        if self.dp_hist_per_val.has_error():
            print(self.dp_hist_per_val.get_error_messages())
        self.assertFalse(self.dp_hist_per_val.has_error())

        if not self.dp_hist_per_val.is_chain_valid():
            print(self.dp_hist_per_val.get_error_messages())
        self.assertTrue(self.dp_hist_per_val.is_chain_valid())

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

        spec_props = self.spec_props_per_val.copy()

        for epsilon_val in [0.1, .25, .65, .431, 1.0]:
            # print(f'> Valid epsilon val: {epsilon_val}')
            spec_props['epsilon'] = epsilon_val
            dp_hist = DPHistogramIntOnePerValueSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        for cl_val in [x[0] for x in astatic.CL_CHOICES]:
            # print(f'> Valid cl val: {cl_val}')
            spec_props['cl'] = cl_val
            dp_hist = DPHistogramIntOnePerValueSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        for good_ds in [1, 2, 10, 100, 56 ** 3, ]:
            spec_props['dataset_size'] = good_ds
            dp_hist = DPHistogramIntOnePerValueSpec(spec_props)
            # print(f'> Valid dataset_size: {good_ds}')
            self.assertTrue(dp_hist.is_chain_valid())

    def test_030_bad_confidence_levels(self):
        """(30) Bad confidence level values"""
        msgt(self.test_030_bad_confidence_levels.__doc__)

        spec_props = self.spec_props_per_val

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

        new_props = self.spec_props_per_val.copy()

        bad_impute_info = [(-10, astatic.ERR_IMPUTE_PHRASE_MIN)]

        for bad_impute, stat_err_msg in bad_impute_info:
            # print(f'> bad impute: {bad_impute}')
            new_props['fixed_value'] = bad_impute
            dp_hist2 = DPHistogramIntOnePerValueSpec(new_props)

            self.assertFalse(dp_hist2.is_chain_valid())
            err_dict = dp_hist2.get_error_msg_dict()
            # print(f"  - {err_dict['message']}")
            self.assertTrue(err_dict['message'].find(stat_err_msg) > -1)

    def test_050_run_dphist_calculation_integer(self):
        """(50) Run DP histogram calculation with integer values"""
        msgt(self.test_050_run_dphist_calculation_integer.__doc__)

        spec_props = {
            'variable': 'Trial',
            'col_index': 4,
            'statistic': astatic.DP_HISTOGRAM,
            astatic.KEY_HIST_BIN_TYPE: astatic.HIST_BIN_TYPE_ONE_PER_VALUE,
            astatic.KEY_HIST_NUMBER_OF_BINS: None,
            astatic.KEY_HIST_BIN_EDGES: None,
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

        num_categories = 9  # expecting 9 categories. 8 + uncategorized
        self.assertEqual(num_categories, len(release_dict['result']['value']['categories']))

        # check that category_value_pairs are included--and that there are 9 of them
        self.assertEqual(num_categories, len(release_dict['result']['value']['category_value_pairs']))

        # Note: much wider than actual range
        expected_accuracy = 5.075173815233827
        self.assertEqual(release_dict['accuracy']['value'], expected_accuracy)

        # Check that the fixed_value is in the list of categories
        #
        fixed_value = release_dict['missing_value_handling']['fixed_value']
        categories = release_dict['result']['value']['categories']
        self.assertTrue(fixed_value in categories)

    def test_060_run_dphist_calculation_integer(self):
        """(60) Run DP histogram calculation with integer values"""
        msgt(self.test_060_run_dphist_calculation_integer.__doc__)

        dp_hist = DPHistogramIntOnePerValueSpec(self.spec_props_per_val)
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
        import json; print(json.dumps(release_dict, indent=4))

        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)

        # expecting 26 categories. 25 + uncategorized
        self.assertEqual(26, len(release_dict['result']['value']['categories']))
        self.assertEqual(26, len(release_dict['result']['value']['category_value_pairs']))

        # accuracy
        expected_accuracy = 6.214608098422191
        self.assertEqual(expected_accuracy, release_dict['accuracy']['value'])

        # Check that the fixed_value is in the list of categories
        #
        fixed_value = release_dict['missing_value_handling']['fixed_value']
        categories = release_dict['result']['value']['categories']
        self.assertTrue(fixed_value in categories)

        # -----------------------------------------------
        # PDF
        # -----------------------------------------------
        samp_full_release_fname = join(DP_REPORTS_TEST_DIR, 'sample_release_01.json')
        self.assertTrue(isfile(samp_full_release_fname))
        samp_full_release_dict = json.load(open(samp_full_release_fname, 'r'))

        # Add newly made statistical release to the full release
        samp_full_release_dict['statistics'] = [release_dict]

        # print('samp_full_release_dict', json.dumps(samp_full_release_dict, indent=4))
        print('Creating test PDF...')
        pdf_maker = PDFReportMaker(samp_full_release_dict)
        if pdf_maker.has_error():
            print(pdf_maker.get_err_msg())
        else:
            output_fname = tempfile.NamedTemporaryFile(
                prefix='report_' + get_timestamp_str(),
                suffix='.pdf',
                delete=True).name
            pdf_maker.save_pdf_to_file(output_fname)
            # print('file written: ', output_fname)
            self.assertTrue(isfile(output_fname))

        self.assertFalse(pdf_maker.has_error())
