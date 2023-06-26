"""
Tests for DPHistogramIntEqualRangesSpec
docker-compose run server python manage.py test opendp_apps.analysis.testing.test_dp_histogram_integer_equal_range_spec.HistogramIntegerEqualRangeStatSpecTest
"""
import copy
import decimal
import json
import os
import tempfile
from os.path import abspath, dirname, isfile, join

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.misc_formatters import get_timestamp_str
from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_histogram_int_equal_ranges_spec import DPHistogramIntEqualRangesSpec
from opendp_apps.dp_reports.pdf_report_maker import PDFReportMaker
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.utils.extra_validators import \
    (VALIDATE_MSG_MORE_BINS_THAN_VALUES, )

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')  # general test data
DP_REPORTS_TEST_DIR = join(dirname(dirname(CURRENT_DIR)), 'dp_reports', 'test_data')  # has sample release
DP_ANALYSIS_TEST_DIR = join(dirname(CURRENT_DIR), 'test_output')  # to write test PDFs (not saved)
if not isfile(DP_ANALYSIS_TEST_DIR):
    os.makedirs(DP_ANALYSIS_TEST_DIR, exist_ok=True)
    print('created: ', DP_ANALYSIS_TEST_DIR)

from unittest import skip
@skip('Reconfiguring for analyst mode')
class HistogramIntegerEqualRangeStatSpecTest(StatSpecTestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):

        super().setUp()

        """Reusable properties for testing basic 'StatSpec' functionality"""
        self.spec_props_bins = {'variable': 'age',
                                'col_index': 1,
                                'statistic': astatic.DP_HISTOGRAM,
                                astatic.KEY_HIST_BIN_TYPE: astatic.HIST_BIN_TYPE_EQUAL_RANGES,
                                astatic.KEY_HIST_NUMBER_OF_BINS: 5,
                                astatic.KEY_HIST_BIN_EDGES: None,
                                'dataset_size': 7000,
                                'epsilon': 1,
                                'delta': 0.0,
                                'cl': astatic.CL_95,
                                astatic.KEY_FIXED_VALUE: 32,
                                astatic.KEY_MISSING_VALUES_HANDLING: astatic.MISSING_VAL_INSERT_FIXED,
                                'variable_info': {
                                    'min': 18,
                                    'max': 68,
                                    'type': pstatic.VAR_TYPE_INTEGER
                                }
                                }

        self.dp_hist_bins = DPHistogramIntEqualRangesSpec(self.spec_props_bins)
        if self.dp_hist_bins.has_error():
            print(self.dp_hist_bins.get_error_messages())
        else:
            pass
            # print('histogram_bin_edges: ', self.dp_hist_bins.histogram_bin_edges)

        self.assertFalse(self.dp_hist_bins.has_error())
        self.assertTrue(self.dp_hist_bins.is_chain_valid())

    def test_001_valid_noise_mechanism(self):
        """(1) Check for the correct noise_mechanism"""
        msgt(self.test_001_valid_noise_mechanism.__doc__)
        dp_hist_int = DPHistogramIntEqualRangesSpec({})
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

        spec_props = self.spec_props_bins.copy()

        for epsilon_val in [0.1, .25, .65, .431, 1.0]:
            # print(f'> Valid epsilon val: {epsilon_val}')
            spec_props['epsilon'] = epsilon_val
            dp_hist = DPHistogramIntEqualRangesSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        for cl_val in [x[0] for x in astatic.CL_CHOICES]:
            # print(f'> Valid cl val: {cl_val}')
            spec_props['cl'] = cl_val
            dp_hist = DPHistogramIntEqualRangesSpec(spec_props)
            self.assertTrue(dp_hist.is_chain_valid())

        for good_ds in [1, 2, 10, 100, 56 ** 3, ]:
            spec_props['dataset_size'] = good_ds
            dp_hist = DPHistogramIntEqualRangesSpec(spec_props)
            # print(f'> Valid dataset_size: {good_ds}')
            self.assertTrue(dp_hist.is_chain_valid())

    def test_030_bad_confidence_levels(self):
        """(30) Bad confidence level values"""
        msgt(self.test_030_bad_confidence_levels.__doc__)

        spec_props = self.spec_props_bins

        def float_range(start, stop, step):
            while start < stop:
                yield float(start)
                start += decimal.Decimal(step)

        for cl_val in list(float_range(-1, 0, '0.1')) + ['alphabet', 'soup']:
            # print(f'> Invalid ci val: {ci_val}')
            spec_props['cl'] = cl_val
            dp_hist = DPHistogramIntEqualRangesSpec(spec_props)
            # print(dp_hist.is_chain_valid())
            valid = dp_hist.is_chain_valid()
            # print(dp_hist.error_messages)
            # print(cl_val)
            self.assertFalse(valid)

    def test_040_test_impute(self):
        """(40) Test impute validation"""
        msgt(self.test_040_test_impute.__doc__)

        new_props = self.spec_props_bins.copy()

        bad_impute_info = [(-10, astatic.ERR_IMPUTE_PHRASE_MIN)]

        for bad_impute, stat_err_msg in bad_impute_info:
            # print(f'> bad impute: {bad_impute}')
            new_props['fixed_value'] = bad_impute
            dp_hist2 = DPHistogramIntEqualRangesSpec(new_props)

            self.assertFalse(dp_hist2.is_chain_valid())
            err_dict = dp_hist2.get_error_msg_dict()
            # print(f"  - {err_dict['message']}")
            self.assertTrue(err_dict['message'].find(stat_err_msg) > -1)

    def test_050_check_bin_errors(self):
        """(50) Check bin errors"""
        msgt(self.test_050_check_bin_errors.__doc__)

        specs = copy.deepcopy(self.spec_props_bins)

        num_bins = 5
        specs[astatic.KEY_HIST_NUMBER_OF_BINS] = num_bins
        specs[astatic.KEY_VARIABLE_INFO]['min'] = 18
        specs[astatic.KEY_VARIABLE_INFO]['max'] = 8

        # Max not greather than min
        dp_hist = DPHistogramIntEqualRangesSpec(specs)
        self.assertTrue(dp_hist.has_error())
        self.assertTrue(dp_hist.get_single_err_msg().find(astatic.ERR_MAX_NOT_GREATER_THAN_MIN) > -1)

        # More bins than values
        specs = copy.deepcopy(self.spec_props_bins)
        num_bins = specs[astatic.KEY_VARIABLE_INFO]['max'] - specs[astatic.KEY_VARIABLE_INFO]['min']
        specs[astatic.KEY_HIST_NUMBER_OF_BINS] = num_bins + 1
        # print('num_bins', num_bins)
        dp_hist = DPHistogramIntEqualRangesSpec(specs)
        self.assertTrue(dp_hist.has_error())
        self.assertTrue(dp_hist.get_single_err_msg().find(VALIDATE_MSG_MORE_BINS_THAN_VALUES) > -1)

    def test_060_check_bin_categories(self):
        """(60) Check bin categories"""
        msgt(self.test_060_check_bin_categories.__doc__)

        specs = copy.deepcopy(self.spec_props_bins)
        dp_hist = DPHistogramIntEqualRangesSpec(specs)
        self.assertEqual(dp_hist.categories,
                         ['[18, 29]', '[30, 42]', '[43, 55]', '[56, 68]', 'uncategorized'])
        self.assertEqual(dp_hist.histogram_bin_edges, [18, 30, 43, 56, 69])

        # print('categories', dp_hist.categories)
        # print('err:', dp_hist.get_single_err_msg())

    def test_070_run_dphist_calculation_int_bins(self):
        """(070) Run DP histogram calculation with 5 bins"""
        msgt(self.test_070_run_dphist_calculation_int_bins.__doc__)

        specs = self.spec_props_bins
        num_bins = 5
        specs[astatic.KEY_HIST_NUMBER_OF_BINS] = num_bins
        specs[astatic.KEY_VARIABLE_INFO]['min'] = 18
        specs[astatic.KEY_VARIABLE_INFO]['max'] = 80

        dp_hist = DPHistogramIntEqualRangesSpec(specs)
        self.assertTrue(dp_hist.is_chain_valid())

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

        # Get the DP Release
        #
        release_dict = dp_hist.get_release_dict()

        # Run some checks
        #
        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)
        # import json; print(json.dumps(release_dict, indent=4))

        # Accuracy
        expected_accuracy = 4.382026634673881
        self.assertEqual(expected_accuracy, release_dict['accuracy']['value'])

        # Check the number of categories and values
        self.assertEqual(num_bins, len(release_dict['result']['value']['categories']))
        self.assertEqual(num_bins, len(release_dict['result']['value']['values']))

        # Check that category_value_pairs are included--and that there are "num_bins"
        self.assertEqual(num_bins, len(release_dict['result']['value']['category_value_pairs']))

        # Check that the fixed_value is in the list of categories
        fixed_value = release_dict['missing_value_handling']['fixed_value']
        self.assertEqual(fixed_value, specs[astatic.KEY_FIXED_VALUE])

        # -----------------------------------------------------
        # Try to create a PDF to make sure that process works
        # -----------------------------------------------------
        print('Creating test PDF...')
        samp_full_release_fname = join(DP_REPORTS_TEST_DIR, 'sample_release_01.json')
        self.assertTrue(isfile(samp_full_release_fname))
        samp_full_release_dict = json.load(open(samp_full_release_fname, 'r'))

        # Add newly made statistical release to the full release
        samp_full_release_dict['statistics'] = [release_dict]

        pdf_maker = PDFReportMaker(samp_full_release_dict)
        if pdf_maker.has_error():
            print(pdf_maker.get_err_msg())
        else:
            output_fname = tempfile.NamedTemporaryFile(
                prefix='report_' + get_timestamp_str(),
                suffix='.pdf',
                delete=True).name
            pdf_maker.save_pdf_to_file(output_fname)
            self.assertTrue(isfile(output_fname))

        self.assertFalse(pdf_maker.has_error())
