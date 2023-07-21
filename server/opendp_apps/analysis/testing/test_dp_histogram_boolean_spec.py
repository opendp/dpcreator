import json
import tempfile
from os.path import abspath, dirname, isfile, join

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.misc_formatters import get_timestamp_str
from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_histogram_boolean_spec import DPHistogramBooleanSpec
from opendp_apps.dp_reports.pdf_report_maker import PDFReportMaker
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import static_vals as pstatic

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')
DP_REPORTS_TEST_DIR = join(dirname(dirname(CURRENT_DIR)), 'dp_reports', 'test_data')  # has sample release


class HistogramBooleanStatSpecTest(StatSpecTestCase):
    """Test the HistogramBooleanStatSpec class"""

    def setUp(self):

        super().setUp()

        """Reusable properties for testing basic 'StatSpec' functionality"""
        self.spec_props = {'variable': 'SMOKING',
                           'col_index': 6,
                           'statistic': astatic.DP_HISTOGRAM,
                           astatic.KEY_HIST_BIN_TYPE: astatic.HIST_BIN_TYPE_ONE_PER_VALUE,
                           # astatic.KEY_HIST_NUMBER_OF_BINS: None,
                           # astatic.KEY_HIST_BIN_EDGES: [18, 25, 35, 45, 55, 65, 75],
                           'dataset_size': 7000,
                           'epsilon': 1.0,
                           'delta': 0.0,
                           'cl': astatic.CL_95,
                           'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                           'fixed_value': 4,
                           'variable_info': {'trueValue': 1,
                                             'falseValue': 2,
                                             'type': pstatic.VAR_TYPE_BOOLEAN},
                           }

        self.spec_props2 = {'variable': 'Havingchild',
                            'col_index': 3,
                            'statistic': astatic.DP_HISTOGRAM,
                            astatic.KEY_HIST_BIN_TYPE: astatic.HIST_BIN_TYPE_ONE_PER_VALUE,
                            'dataset_size': 7000,
                            'epsilon': 1.0,
                            'delta': 0.0,
                            'cl': astatic.CL_95,
                            'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                            'fixed_value': 2,
                            'variable_info': {'trueValue': 1,
                                              'falseValue': 2,
                                              'type': pstatic.VAR_TYPE_BOOLEAN},
                            }

        self.dp_hist = DPHistogramBooleanSpec(self.spec_props)

        if self.dp_hist.has_error():
            print(self.dp_hist.get_error_messages())
        self.assertFalse(self.dp_hist.has_error())
        self.assertTrue(self.dp_hist.is_chain_valid())

    def test_001_valid_noise_mechanism(self):
        """(1) Check for the correct noise_mechanism"""
        msgt(self.test_001_valid_noise_mechanism.__doc__)

        self.assertEqual(self.dp_hist.noise_mechanism, astatic.NOISE_GEOMETRIC_MECHANISM)

    # @skip('skip')
    def test_040_test_impute(self):
        """(40) Test impute validation"""
        msgt(self.test_040_test_impute.__doc__)

        spec_props = self.spec_props.copy()

        dp_hist = DPHistogramBooleanSpec(spec_props)
        if not dp_hist.is_chain_valid():
            print(dp_hist.get_error_messages())
        self.assertTrue(dp_hist.is_chain_valid())

    def test_050_test_impute_unknown_fixed_value(self):
        """(50) Test impute validation, unknown fixed value is actually okay here"""
        msgt(self.test_050_test_impute_unknown_fixed_value.__doc__)

        spec_props = self.spec_props.copy()
        spec_props['fixed_value'] = 'not-a-known-category'

        dp_hist = DPHistogramBooleanSpec(spec_props)
        if not dp_hist.is_chain_valid():
            print(dp_hist.get_error_messages())
        self.assertTrue(dp_hist.is_chain_valid())

    def test_060_test_true_false_values_equal(self):
        """(60) The true and false values should not be equal"""
        msgt(self.test_060_test_true_false_values_equal.__doc__)

        spec_props = self.spec_props.copy()
        spec_props['variable_info']['trueValue'] = 'same-as-before'
        spec_props['variable_info']['falseValue'] = 'same-as-before'

        dp_hist = DPHistogramBooleanSpec(spec_props)
        # if not dp_hist.is_chain_valid(): print(dp_hist.get_error_messages())

        self.assertFalse(dp_hist.is_chain_valid())
        self.assertTrue(dp_hist.get_single_err_msg().find(astatic.ERR_BOOL_TRUE_FALSE_NOT_EQUAL) > -1)

    def test_100_run_dphist_calculation_boolean(self):
        """(100) Run DP histogram calculation"""
        msgt(self.test_100_run_dphist_calculation_boolean.__doc__)

        dp_hist = self.dp_hist
        # ------------------------------------------------------
        # Run the actual mean
        # ------------------------------------------------------
        # Column indexes - We know this data has 20 columns
        col_indexes = [idx for idx in range(0, 10)]

        # File object
        #
        teacher_survey_filepath = join(TEST_DATA_DIR, 'teacher_survey', 'teacher_survey.csv')
        self.assertTrue(isfile(teacher_survey_filepath))

        file_obj = open(teacher_survey_filepath, 'r')

        # Call run_chain
        #
        dp_hist.run_chain(col_indexes, file_obj, sep_char=",")
        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)

        release_dict = dp_hist.get_release_dict()
        # import json; print(json.dumps(release_dict, indent=4))

        # Check that the fixed_value and list of categories are "unquoted"
        #
        release_fixed_value = release_dict['missing_value_handling']['fixed_value']
        self.assertEqual(release_fixed_value, dp_hist.fixed_value)

        categories = release_dict['result']['value']['categories']
        self.assertEqual(categories[:2], dp_hist.get_unformatted_boolean_categories())

    def test_110_run_dphist_calculation_boolean(self):
        """(110) Run DP histogram calculation on another column"""
        msgt(self.test_110_run_dphist_calculation_boolean.__doc__)

        dp_hist = DPHistogramBooleanSpec(self.spec_props2)
        self.assertTrue(dp_hist.is_chain_valid())
        # ------------------------------------------------------
        # Run the actual mean
        # ------------------------------------------------------
        # Column indexes - We know this data has 20 columns
        col_indexes = [idx for idx in range(0, 10)]

        # File object
        #
        teacher_survey_filepath = join(TEST_DATA_DIR, 'teacher_survey', 'teacher_survey.csv')
        self.assertTrue(isfile(teacher_survey_filepath))

        file_obj = open(teacher_survey_filepath, 'r')

        # Call run_chain
        #
        dp_hist.run_chain(col_indexes, file_obj, sep_char=",")
        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)

        release_dict = dp_hist.get_release_dict()
        # import json; print(json.dumps(release_dict, indent=4))

        # Check the fixed_value
        #
        release_fixed_value = release_dict['missing_value_handling']['fixed_value']
        self.assertEqual(release_fixed_value, dp_hist.fixed_value)

        # Check the list of categories
        #
        categories = release_dict['result']['value']['categories']
        self.assertEqual(categories[:2], dp_hist.get_unformatted_boolean_categories())

        # Check the accuracy
        #
        accuracy_val = release_dict['accuracy']['value']
        self.assertEqual(accuracy_val, 3.6888794541139363)

    def test_120_run_dphist_boolean_on_nonbool_field(self):
        """(120) Run DP histogram on the marriage field which has 8 possible values but force 2 values
        Actual categories:
            1- Single
            2- Steady Relationship
            3- Living with partner
            4- Married first time
            5- Remarried
            6- Separated
            7- Divorced
            8- Widowed

        Forced categories:
            1- True
            4- False
            everything else - uncategorized
        """
        msgt(self.test_120_run_dphist_boolean_on_nonbool_field.__doc__)

        spec_props_not_boolean = {'variable': 'maritalstatus',
                                  'col_index': 2,
                                  'statistic': astatic.DP_HISTOGRAM,
                                  astatic.KEY_HIST_BIN_TYPE: astatic.HIST_BIN_TYPE_ONE_PER_VALUE,
                                  'dataset_size': 7000,
                                  'epsilon': 1.0,
                                  'delta': 0.0,
                                  'cl': astatic.CL_95,
                                  'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                                  'fixed_value': 2,
                                  'variable_info': {'trueValue': 1,
                                                    'falseValue': 4,
                                                    'type': pstatic.VAR_TYPE_BOOLEAN},
                                  }

        dp_hist = DPHistogramBooleanSpec(spec_props_not_boolean)
        self.assertTrue(dp_hist.is_chain_valid())
        # ------------------------------------------------------
        # Run the actual mean
        # ------------------------------------------------------
        # Column indexes - We know this data has 20 columns
        col_indexes = [idx for idx in range(0, 10)]

        # File object
        #
        teacher_survey_filepath = join(TEST_DATA_DIR, 'teacher_survey', 'teacher_survey.csv')
        self.assertTrue(isfile(teacher_survey_filepath))

        file_obj = open(teacher_survey_filepath, 'r')

        # Call run_chain
        #
        dp_hist.run_chain(col_indexes, file_obj, sep_char=",")
        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)

        release_dict = dp_hist.get_release_dict()
        # import json; print(json.dumps(release_dict, indent=4))

        # Check the fixed_value
        #
        release_fixed_value = release_dict['missing_value_handling']['fixed_value']
        self.assertEqual(release_fixed_value, dp_hist.fixed_value)

        # Check the list of categories
        #
        categories = release_dict['result']['value']['categories']
        self.assertEqual(categories[:2], dp_hist.get_unformatted_boolean_categories())

        # Check the accuracy
        #
        accuracy_val = release_dict['accuracy']['value']
        self.assertEqual(accuracy_val, 3.6888794541139363)

        # The number of uncategorized should be greater than the True value for this dataset
        #
        val_true = release_dict['result']['value']['values'][0]
        val_uncategorized = release_dict['result']['value']['values'][1]
        self.assertTrue(val_uncategorized > val_true)

        # ----------------------------------
        # PDF
        # ----------------------------------
        samp_full_release_fname = join(DP_REPORTS_TEST_DIR,
                                       'sample_histogram_release.json')
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
            # _output_fname = 'hist01.pdf'
            output_fname = tempfile.NamedTemporaryFile(
                prefix='report_' + get_timestamp_str(),
                suffix='.pdf',
                delete=True).name
            pdf_maker.save_pdf_to_file(output_fname)
            # print('file written: ', output_fname)
            self.assertTrue(isfile(output_fname))

        self.assertFalse(pdf_maker.has_error())

    def test_130_run_dphist_calculation_boolean_str(self):
        """(130) Run DP histogram on boolean string data"""
        msgt(self.test_130_run_dphist_calculation_boolean_str.__doc__)

        spec_props = {'variable': 'Language',
                      'col_index': 1,
                      'statistic': astatic.DP_HISTOGRAM,
                      astatic.KEY_HIST_BIN_TYPE: astatic.HIST_BIN_TYPE_ONE_PER_VALUE,
                      'dataset_size': 183,
                      'epsilon': 1.0,
                      'delta': 0.0,
                      'cl': astatic.CL_95,
                      'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                      'fixed_value': '"DA"',
                      'variable_info': {'trueValue': '"EN"',
                                        'falseValue': '"DA"',
                                        'type': pstatic.VAR_TYPE_BOOLEAN},
                      }

        dp_hist = DPHistogramBooleanSpec(spec_props)
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

        # Check that the fixed_value and list of categories are "unquoted"
        #
        release_fixed_value = release_dict['missing_value_handling']['fixed_value']
        self.assertEqual(release_fixed_value, dp_hist.fixed_value)

        categories = release_dict['result']['value']['categories']
        self.assertEqual(categories[:2], dp_hist.get_unformatted_boolean_categories())
