"""
docker-compose run server python manage.py test opendp_apps.analysis.testing.test_dp_histogram_integer_spec.HistogramIntegerStatSpecTest
"""
import copy
import decimal
import json
import os
import tempfile
import unittest
from os.path import abspath, dirname, isfile, join

import pandas as pd
from opendp.accuracy import laplacian_scale_to_accuracy

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.misc_formatters import get_timestamp_str
from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.tools.dp_histogram_int_equal_ranges_spec import DPHistogramIntEqualRangesSpec
from opendp_apps.analysis.tools.dp_histogram_int_one_per_value_spec import DPHistogramIntOnePerValueSpec
from opendp_apps.analysis.tools.dp_histogram_int_bin_edges_spec import DPHistogramIntBinEdgesSpec
from opendp_apps.dp_reports.pdf_report_maker import PDFReportMaker
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import static_vals as pstatic

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
                                    # 'min': 0,
                                    # 'max': 100,
                                    'min': 18,
                                    'max': 68,
                                    'type': pstatic.VAR_TYPE_INTEGER
                                }
                                }

        self.dp_hist_bins = DPHistogramIntEqualRangesSpec(self.spec_props_bins)
        if self.dp_hist_bins.has_error():
            print(self.dp_hist_bins.get_error_messages())
        else:
            print('histogram_bin_edges: ', self.dp_hist_bins.histogram_bin_edges)

        self.assertFalse(self.dp_hist_bins.has_error())
        self.assertTrue(self.dp_hist_bins.is_chain_valid())

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

    def test_140_run_dphist_calculation_int_bins(self):
        """(140) Run DP histogram calculation with 7 bins"""
        msgt(self.test_140_run_dphist_calculation_int_bins.__doc__)

        specs = copy.deepcopy(self.spec_props_bins)
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

        release_dict = dp_hist.get_release_dict()

        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)
        print(dp_hist.get_success_msg_dict())

        # expecting (num_bins - 1)  + (1 for uncategorized) = num_bins
        self.assertEqual(num_bins, len(release_dict['result']['value']['categories']))

        self.assertEqual(num_bins, len(release_dict['result']['value']['values']))

        # check that category_value_pairs are included--and that there are "num_bins"
        self.assertEqual(num_bins, len(release_dict['result']['value']['category_value_pairs']))

        # Check that the fixed_value is in the list of categories
        #
        fixed_value = release_dict['missing_value_handling']['fixed_value']
        self.assertEqual(fixed_value, specs[astatic.KEY_FIXED_VALUE])

        # -----------------------------------------------
        # PDF
        # -----------------------------------------------
        samp_full_release_fname = join(DP_REPORTS_TEST_DIR, 'sample_release_01.json')
        self.assertTrue(isfile(samp_full_release_fname))
        samp_full_release_dict = json.load(open(samp_full_release_fname, 'r'))

        # Add newly made statistical release to the full release
        samp_full_release_dict['statistics'] = [release_dict]

        # print('samp_full_release_dict', json.dumps(samp_full_release_dict, indent=4))
        # print('Creating PDF...')
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
            # self.assertTrue(isfile(output_fname))

        self.assertFalse(pdf_maker.has_error())

    def test_150_run_dphist_bins(self):
        """(150) Hist with bins"""
        msgt(self.test_150_run_dphist_bins.__doc__)

        from opendp.trans import make_count_by_categories, make_find_bin
        from opendp.meas import make_base_discrete_laplace
        from opendp.typing import VectorDomain, AllDomain, usize
        from opendp.mod import binary_search_chain

        edges = [1., 3.14159, 4., 7.]
        preprocess = (
                make_find_bin(edges=edges) >>
                make_count_by_categories(categories=list(range(len(edges))), TIA=usize)
        )

        noisy_histogram_from_dataframe = binary_search_chain(
            lambda s: preprocess >> make_base_discrete_laplace(s, D=VectorDomain[AllDomain[int]]),
            d_in=1, d_out=1.)

        assert noisy_histogram_from_dataframe.check(1, 1.)
        import numpy as np
        data = np.random.uniform(0., 10., size=100)

        print(noisy_histogram_from_dataframe(data))
        print(noisy_histogram_from_dataframe(data))
        print(noisy_histogram_from_dataframe(data))

    @unittest.skip('not ready')
    def test_150_run_dphist_bins(self):
        """(150) Hist with bins"""
        msgt(self.test_150_run_dphist_bins.__doc__)

        from opendp.trans import make_count_by_categories, make_find_bin
        from opendp.meas import make_base_discrete_laplace
        from opendp.typing import VectorDomain, AllDomain, usize
        from opendp.mod import binary_search_chain

        # edges = [1., 3.14159, 4., 7.]
        edges = self.dp_hist_bins.histogram_bin_edges
        edges = [int(x) for x in edges]
        print('edges', edges)

        preprocess = (
                make_find_bin(edges=edges) >>
                make_count_by_categories(categories=list(range(len(edges))), TIA=usize)
        )

        noisy_histogram_from_dataframe = binary_search_chain(
            lambda s: preprocess >> make_base_discrete_laplace(s, D=VectorDomain[AllDomain[int]]),
            d_in=1, d_out=self.dp_hist_bins.epsilon)

        print(laplacian_scale_to_accuracy(noisy_histogram_from_dataframe, .01))

        assert noisy_histogram_from_dataframe.check(1, self.dp_hist_bins.epsilon)
        import numpy as np
        # data = np.random.uniform(0., 10., size=100)

        teacher_survey_filepath = join(TEST_DATA_DIR, 'teacher_survey', 'teacher_survey.csv')
        self.assertTrue(isfile(teacher_survey_filepath))
        df = pd.read_csv(teacher_survey_filepath)
        # df['age'] = df['age'].astype(float)

        print(df.columns)
        # data = np.random.uniform(self.dp_hist_bins.min,
        #                         self.dp_hist_bins.max,
        #                         size=100)
        data = df['age'].tolist()
        print('actual min: ', min(data))
        print('actual max: ', max(data))

        data = data[:50]
        data.sort()
        print('data', data)

        print('edges:', edges)
        print('\n-- DP histogram --')
        for x in range(1, 4):
            noisy_hist = noisy_histogram_from_dataframe(data)
            print(noisy_hist, type(noisy_hist))

        print('\n-- np.histogram --')
        print(np.histogram(data, bins=edges, range=(18, 68)))

    def test_160_run_dphist_int_edges(self):
        """(160) Run DP histogram calculation with edges"""
        msgt(self.test_160_run_dphist_int_edges.__doc__)

        spec_props = {'variable': 'age',
                      'col_index': 1,
                      'statistic': astatic.DP_HISTOGRAM,
                      astatic.KEY_HIST_BIN_TYPE: astatic.HIST_BIN_TYPE_BIN_EDGES,
                      astatic.KEY_HIST_NUMBER_OF_BINS: None,
                      astatic.KEY_HIST_BIN_EDGES: [18, 25, 35, 45, 55, 65, 75],
                      'dataset_size': 7000,
                      'epsilon': 1,
                      'delta': 0.0,
                      'cl': astatic.CL_95,
                      astatic.KEY_FIXED_VALUE: 32,
                      astatic.KEY_MISSING_VALUES_HANDLING: astatic.MISSING_VAL_INSERT_FIXED,
                      'variable_info': {
                        'min': 18,
                        'max': 75,
                        'type': pstatic.VAR_TYPE_INTEGER
                        }
                      }

        dp_hist = DPHistogramIntBinEdgesSpec(spec_props)

        if not dp_hist.is_chain_valid():
            print('Error!')
            print(dp_hist.get_single_err_msg())
        else:
            print('Validated!')
            print(dp_hist.get_success_msg_dict())

        # ------------------------------------------------------
        # Run the actual histogram
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

        if dp_hist.has_error():
            print('Error: ', dp_hist.has_error())

        release_dict = dp_hist.get_release_dict()
        # import json; print(json.dumps(release_dict, indent=4))

        self.assertFalse(dp_hist.has_error())
        self.assertTrue('categories' in dp_hist.value)
        self.assertTrue('values' in dp_hist.value)

        expected_num_bins = 7
        # expecting (num_bins - 1)  + (1 for uncategorized) = num_bins
        self.assertEqual(expected_num_bins, len(release_dict['result']['value']['categories']))

        self.assertEqual(expected_num_bins, len(release_dict['result']['value']['values']))

        # check that category_value_pairs are included--and that there are "num_bins"
        self.assertEqual(expected_num_bins, len(release_dict['result']['value']['category_value_pairs']))

        # Check that the fixed_value is in the list of categories
        #
        fixed_value = release_dict['missing_value_handling']['fixed_value']
        self.assertEqual(fixed_value, spec_props[astatic.KEY_FIXED_VALUE])

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
            # self.assertTrue(isfile(output_fname))

        self.assertFalse(pdf_maker.has_error())


"""
docker-compose run server python manage.py test opendp_apps.analysis.testing.test_dp_histogram_integer_spec.HistogramIntegerStatSpecTest.test_160_run_dphist_bins
"""
