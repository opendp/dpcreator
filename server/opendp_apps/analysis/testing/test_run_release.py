import json
from os.path import abspath, dirname, isfile, join

from django.core import mail
from django.core.files import File
from django.test import override_settings
from rest_framework.reverse import reverse as drf_reverse
from rest_framework.test import APIClient

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.models import AnalysisPlan, AuxiliaryFileDepositRecord, ReleaseEmailRecord
from opendp_apps.analysis.release_info_formatter import ReleaseInfoFormatter
from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.validate_release_util import ValidateReleaseUtil
from opendp_apps.dataset.dataset_formatter import DataSetFormatter
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.utils.extra_validators import VALIDATE_MSG_EPSILON

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from unittest import skip


@skip('Reconfiguring for analyst mode')
class TestRunRelease(StatSpecTestCase):
    # fixtures = ['test_dataset_data_001.json']

    def setUp(self):
        super().setUp()

        # test client
        self.client = APIClient()

        # self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        self.client.force_login(self.user_obj)

        # dataset_info = DataSetInfo.objects.get(id=4)
        # self.add_source_file(dataset_info, 'Fatigue_data.tab', True)

        # plan_info = AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        # self.assertTrue(plan_info.success)
        # orig_plan = plan_info.data

        # plan_info = self.get_release_plan()
        # Retrieve it
        #
        self.analysis_plan = self.retrieve_new_plan()
        # self.assertEqual(orig_plan.object_id, self.analysis_plan.object_id)

        self.analysis_plan.variable_info['EyeHeight']['min'] = -8.01
        self.analysis_plan.variable_info['EyeHeight']['max'] = 5

        self.analysis_plan.variable_info['TypingSpeed']['min'] = 3
        self.analysis_plan.variable_info['TypingSpeed']['max'] = 30

        # analysis_plan.variable_info = variable_info_mod
        self.analysis_plan.save()

        self.general_stat_specs = [
            {
                "statistic": astatic.DP_MEAN,
                "variable": "EyeHeight",
                "epsilon": .25,
                "delta": 0,
                "cl": astatic.CL_95,
                "error": "",
                "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                "handle_as_fixed": False,
                "fixed_value": "1",
                "locked": False,
                "label": "EyeHeight",
                "variable_info": {
                    "min": 0,
                    "max": 100,
                    "type": pstatic.VAR_TYPE_FLOAT
                }
            },
            {
                "statistic": astatic.DP_MEAN,
                "variable": "TypingSpeed",
                "epsilon": .25,
                "delta": 0,
                "cl": astatic.CL_99,
                "error": "",
                "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                "handle_as_fixed": False,
                "fixed_value": "9",
                "locked": False,
                "label": "TypingSpeed",
                "variable_info": {
                    "min": 0,
                    "max": 100,
                    "type": pstatic.VAR_TYPE_FLOAT
                }
            },
            {
                'variable': 'Subject',
                'col_index': 0,
                'statistic': astatic.DP_HISTOGRAM,
                'dataset_size': 183,
                'epsilon': 0.5,
                'delta': 0.0,
                'cl': astatic.CL_95,
                'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                'fixed_value': 'ac',
                'variable_info': {
                    'categories': ['ac', 'kj', 'ys', 'bh1', 'bh2', 'jm', 'mh', 'cw',
                                   'jp', 'rh', 'aq', 'ph', 'le', 'mn', 'ls2', 'no', 'af'],
                    'type': pstatic.VAR_TYPE_CATEGORICAL
                }
            }
        ]

    def add_source_file(self, dataset_info: DataSetInfo, filename: str, add_profile: bool = False) -> DataSetInfo:
        """Add a source file -- example...
        - filepath - file under dpcreator/test_data
        """

        # File to attach: Must be in "dpcreator/test_data"
        #
        filepath = join(TEST_DATA_DIR, filename)
        self.assertTrue(isfile(filepath))

        # Attach the file to the  `dataset_info.source_file` field
        #
        django_file = File(open(filepath, 'rb'))
        dataset_info.source_file.save(filename, django_file)
        dataset_info.save()

        # If specified, profile the file
        #
        if add_profile is True:
            profile_handler = profiler_tasks.run_profile_by_filefield(dataset_info.object_id)
            # print('profile_handler.has_error()', profile_handler.has_error())

            # Shouldn't have errors
            if profile_handler.has_error():
                print(f'!! error: {profile_handler.get_err_msg()}')

            self.assertTrue(profile_handler.has_error() is False)

        # re-retrieve it...
        return DataSetInfo.objects.get(object_id=dataset_info.object_id)

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_10_compute_stats(self):
        """(10) Run compute stats"""
        msgt(self.test_10_compute_stats.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = [self.general_stat_specs[2]]
        analysis_plan.save()

        analysis_plan2 = AnalysisPlan.objects.get(object_id=analysis_plan.object_id)
        print('analysis_plan.dp_statistics - after save', analysis_plan2.dp_statistics)

        # Check the basics
        #
        release_util = ValidateReleaseUtil.compute_mode(
            self.user_obj,
            analysis_plan.object_id,
            run_dataverse_deposit=False)

        if release_util.has_error():
            print('release_util:', release_util.get_err_msg())
        self.assertFalse(release_util.has_error())
        return

        release_info_object = release_util.get_new_release_info_object()
        dp_release = release_info_object.dp_release

        stats_list = dp_release['statistics']

        self.assertEqual(stats_list[0]['variable'], 'EyeHeight')
        self.assertTrue('result' in stats_list[0])
        self.assertTrue('value' in stats_list[0]['result'])
        self.assertTrue(float(stats_list[0]['result']['value']))

        self.assertEqual(stats_list[1]['variable'], 'TypingSpeed')
        self.assertTrue('result' in stats_list[1])
        self.assertTrue('value' in stats_list[1]['result'])
        self.assertTrue(float(stats_list[1]['result']['value']))

    def test_30_api_bad_stat(self):
        """(30) Via API, run compute stats with error"""
        msgt(self.test_30_api_bad_stat.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        self.general_stat_specs[0]['epsilon'] = 1.2
        analysis_plan.dp_statistics = self.general_stat_specs
        analysis_plan.save()

        params = dict(object_id=str(analysis_plan.object_id))
        response = self.client.post('/api/release/',
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        print('jresp', jresp)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(jresp['success'])
        self.assertTrue(jresp['message'].find(VALIDATE_MSG_EPSILON) > -1)

    def test_40_api_bad_overall_epsilon(self):
        """(30) Via API, run compute stats, bad overall epsilon"""
        msgt(self.test_40_api_bad_overall_epsilon.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = self.general_stat_specs
        analysis_plan.save()

        # Put some bad data in!
        setup_info = analysis_plan.dataset.get_depositor_setup_info()
        setup_info.epsilon = None  # Shouldn't happen but what if it does!
        setup_info.save()

        params = dict(object_id=str(analysis_plan.object_id))
        response = self.client.post('/api/release/',
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        # print('jresp', jresp)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(jresp['success'])
        self.assertTrue(jresp['message'].find(astatic.ERR_MSG_BAD_TOTAL_EPSILON) > -1)

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_50_success(self):
        """(50) Via API, run compute stats successfully"""
        msgt(self.test_50_success.__doc__)

        analysis_plan = self.analysis_plan

        # The source_file should exist
        self.assertTrue(analysis_plan.dataset.source_file)

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = [self.general_stat_specs[2],
                                       self.general_stat_specs[1]]  # , self.general_stat_specs[2]]
        analysis_plan.save()

        analysis_plan2 = AnalysisPlan.objects.get(object_id=analysis_plan.object_id)

        params = dict(object_id=str(analysis_plan2.object_id))

        response = self.client.post('/api/release/',
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        # print('jresp', json.dumps(jresp, indent=4))
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(jresp['dp_release'])
        self.assertIsNotNone(jresp['object_id'])

        updated_plan = AnalysisPlan.objects.get(object_id=analysis_plan2.object_id)
        json_filename = ReleaseInfoFormatter.get_json_filename(updated_plan.release_info)

        # Check on the DP Release JSON file
        # File exists and has a size
        self.assertTrue(updated_plan.release_info.dp_release_json_file.name.endswith(json_filename))
        self.assertTrue(updated_plan.release_info.dp_release_json_file.size >= 2600)

        self.assertTrue(updated_plan.release_info.dv_json_deposit_complete is False)
        self.assertTrue(updated_plan.release_info.dv_pdf_deposit_complete is False)

        # Check that the AuxiliaryFileDepositRecord objects are correct
        #
        self.assertTrue(AuxiliaryFileDepositRecord.objects.filter(release_info=updated_plan.release_info).count() > 0)
        for dep_rec in AuxiliaryFileDepositRecord.objects.filter(release_info=updated_plan.release_info):
            self.assertTrue(dep_rec.deposit_success is False)
            self.assertTrue(dep_rec.http_status_code == 403 or \
                            dep_rec.http_status_code < 0)

        # The source_file should be deleted
        analysis_plan = AnalysisPlan.objects.get(id=analysis_plan.id)
        self.assertTrue(not analysis_plan.dataset.source_file)

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_55_success_download_urls(self):
        """(55) Test PDF and JSOn download Urls"""
        msgt(self.test_55_success_download_urls.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = self.general_stat_specs
        analysis_plan.save()

        params = dict(object_id=str(analysis_plan.object_id))

        response = self.client.post('/api/release/',
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        # print('jresp', jresp)
        self.assertEqual(response.status_code, 201)

        updated_plan = AnalysisPlan.objects.get(object_id=analysis_plan.object_id)

        print('>> updated_plan.variable_info', updated_plan.variable_info)

        # ------------------------------------
        # (1) JSON file download url
        # ------------------------------------

        # (1a) Url should exist....
        release_info_object_id = str(updated_plan.release_info.object_id)
        expected_url = drf_reverse('release-download-json', args=[], kwargs=dict(pk=release_info_object_id))
        self.assertEqual(expected_url, updated_plan.release_info.download_json_url())

        # (1b) Delete file, url should no longer exist
        updated_plan.release_info.dp_release_json_file.delete()
        updated_plan.release_info.save()
        self.assertIsNone(updated_plan.release_info.download_json_url())

        # ------------------------------------
        # (2) PDF file download url
        # ------------------------------------

        # (2a) The PDF file url is not generated in this test and should be None
        # self.assertIsNotNone(updated_plan.release_info.download_pdf_url())

        # ------------------------------------------------------
        # (2b) Artificially add a PDF file to the ReleaseInfo object
        #  and check that it a proper url is generated
        # ------------------------------------------------------
        fname_blank = 'near_blank_for_tests.pdf'
        filepath = join(TEST_DATA_DIR, 'pdfs', fname_blank)
        self.assertTrue(isfile(filepath))

        # Attach the file to the `release_info.dp_release_pdf_file` field
        #
        django_file = File(open(filepath, 'rb'))
        updated_plan.release_info.dp_release_pdf_file.save(fname_blank, django_file)
        updated_plan.release_info.save()

        # Now a url should be available
        #
        expected_pdf_url = drf_reverse('release-download-pdf', args=[], kwargs=dict(pk=release_info_object_id))
        self.assertEqual(expected_pdf_url, updated_plan.release_info.download_pdf_url())

        # The source_file should be deleted
        self.assertTrue(not analysis_plan.dataset.source_file)

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_60_analysis_plan_has_release_info(self):
        """(60) Via API, ensure that release_info is added as a field to AnalysisPlan"""
        msgt(self.test_60_analysis_plan_has_release_info.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = self.general_stat_specs
        analysis_plan.save()

        params = dict(object_id=str(analysis_plan.object_id))
        response = self.client.post('/api/release/',
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        print('jresp-->', jresp)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(jresp['dp_release'])
        self.assertIsNotNone(jresp['object_id'])

        response = self.client.get(f'/api/analyze/{analysis_plan.object_id}/')
        analysis_plan_jresp = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(analysis_plan_jresp['release_info'])

        # print(json.dumps(analysis_plan_jresp, indent=4))
        histogram_results = list(filter(lambda x: x['statistic'] == 'histogram',
                                        analysis_plan_jresp['release_info']['dp_release']['statistics']))
        self.assertIsNotNone(histogram_results)

        # print(json.dumps(histogram_results, indent=4))
        self.assertTrue(type(histogram_results[0]['result']), dict)
        histogram_values = histogram_results[0]['result']['value']
        self.assertTrue('categories' in histogram_values)
        self.assertTrue('values' in histogram_values)

        self.assertIn('dp_release', analysis_plan_jresp['release_info'])

        self.assertIn('dataset', analysis_plan_jresp['release_info']['dp_release'])

        updated_plan = AnalysisPlan.objects.get(object_id=self.analysis_plan.object_id)
        json_filename = ReleaseInfoFormatter.get_json_filename(updated_plan.release_info)

        self.assertTrue(updated_plan.release_info.dp_release_json_file.name.endswith(json_filename))
        self.assertTrue(updated_plan.release_info.dp_release_json_file.size >= 2600)

        # Check that the AuxiliaryFileDepositRecord objects are correct
        #
        self.assertTrue(AuxiliaryFileDepositRecord.objects.filter(release_info=updated_plan.release_info).count() > 0)
        for dep_rec in AuxiliaryFileDepositRecord.objects.filter(release_info=updated_plan.release_info):
            self.assertTrue(dep_rec.deposit_success is False)
            self.assertTrue(dep_rec.http_status_code == 403 or \
                            dep_rec.http_status_code < 0)

        # Uncomment next line to show the AnalysisPlan output
        #   with attached ReleaseInfo object
        # print(json.dumps(analysis_plan_jresp, indent=4))

        # The source_file should be deleted
        self.assertTrue(not analysis_plan.dataset.source_file)

    def test_70_dataset_formatter_eye_fatigue_file(self):
        """(70) Test the DataSetFormatter -- dataset info formatted for inclusion in ReleaseInfo.dp_release"""
        msgt(self.test_70_dataset_formatter_eye_fatigue_file.__doc__)
        """
        Expected result:
        {
            "type": "dataverse",
            "name": "Replication Data for: Eye-typing experiment",
            "citation": null,
            "doi": "doi:10.7910/DVN/PUXVDH",
            "identifier": null,
            "installation": {
                "name": "Mock Local Dataverse",
                "url": "http://127.0.0.1:8000/dv-mock-api"
            },
            "file_information": {
                "name": "Fatigue_data.tab",
                "identifier": null,
                "fileFormat": "text/tab-separated-values"
            }
        }
        """
        formatter = DataSetFormatter(self.analysis_plan.dataset)
        if formatter.has_error():
            print(formatter.get_err_msg())

        self.assertFalse(formatter.has_error())
        ds_info = formatter.get_formatted_info()

        self.assertEqual(ds_info['type'], "dataverse")
        self.assertEqual(ds_info['name'], "Replication Data for: Eye-typing experiment")
        self.assertIsNone(ds_info['citation'])

        self.assertEqual(ds_info['doi'], "doi:10.7910/DVN/PUXVDH")
        self.assertIsNone(ds_info['identifier'])

        self.assertEqual(ds_info['installation']['name'], 'Mock Local Dataverse')
        self.assertEqual(ds_info['installation']['url'], 'http://127.0.0.1:8000/dv-mock-api')

        self.assertEqual(ds_info['file_information']['name'], "Fatigue_data.tab")
        self.assertIsNone(ds_info['file_information']['identifier'])
        self.assertEqual(ds_info['file_information']['fileFormat'], "text/tab-separated-values")

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_80_dataset_formatter_crisis_file(self):
        """(80) Test the DataSetFormatter -- dataset info formatted for inclusion in ReleaseInfo.dp_release"""
        msgt(self.test_80_dataset_formatter_crisis_file.__doc__)
        """
        Expected result:
        {
            "type": "dataverse",
            "name": "crisis.tab",
            "citation": "Epstein, Lee, Daniel E Ho, Gary King, and Jeffrey A Segal. 2005. The 
            Supreme Court During Crisis: How War Affects only Non-War Cases. New York University
             Law Review 80: 1\u2013116: \n<a href=\"http://j.mp/kh2NV8\" target=\"_blank\" 
             rel=\"nofollow\">Link to article</a>. DASH",
            "doi": "doi:10.7910/DVN/OLD7MB",
            "identifier": null,
            "release_deposit_info": {
                "deposited": false
            },
            "installation": {
                "name": "Harvard Dataverse",
                "url": "https://dataverse.harvard.edu"
            },
            "file_information": {
                "name": "crisis.tab",
                "identifier": "https://doi.org/10.7910/DVN/OLD7MB/ZI4N3J",
                "fileFormat": "text/tab-separated-values"
            }
        }
        """
        dataset_info = DataSetInfo.objects.get(id=3)

        formatter = DataSetFormatter(dataset_info)
        if formatter.has_error():
            print(formatter.get_err_msg())

        self.assertFalse(formatter.has_error())
        ds_info = formatter.get_formatted_info()
        # print(json.dumps(ds_info, indent=4))

        self.assertEqual(ds_info['type'], "dataverse")
        self.assertEqual(ds_info['name'], "crisis.tab")
        self.assertTrue(ds_info['citation'].startswith("Epstein, Lee"))

        self.assertEqual(ds_info['doi'], "doi:10.7910/DVN/OLD7MB")
        self.assertIsNone(ds_info['identifier'])

        self.assertEqual(ds_info['installation']['name'], 'Harvard Dataverse')
        self.assertEqual(ds_info['installation']['url'], 'https://dataverse.harvard.edu')

        self.assertEqual(ds_info['file_information']['name'], "crisis.tab", )
        self.assertEqual(ds_info['file_information']['identifier'], "https://doi.org/10.7910/DVN/OLD7MB/ZI4N3J")
        self.assertEqual(ds_info['file_information']['fileFormat'], "text/tab-separated-values")

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_90_dp_count_pums_data(self):
        """
        (90) Via API, Test DP Count with PUMS data.
        Note: This is very hack! A full DataSetInfo object with related objects should be saved as a separate fixture
        """
        msgt(self.test_90_dp_count_pums_data.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)

        # Hack 1: Update to the PUMS data profile
        dataset_info.data_profile = {"self": {"created_at": "2021-10-04 15:20:00",
                                              "description": "TwoRavens metadata generated by https://github.com/TwoRavens/raven-metadata-service"},
                                     "$schema": "https://github.com/TwoRavens/raven-metadata-service/schema/jsonschema/1-2-0.json#",
                                     "dataset": {"rowCount": 10000, "variableCount": 11,
                                                 "variableOrder": [[0, "X"], [1, "state"], [2, "puma"], [3, "sex"],
                                                                   [4, "age"], [5, "educ"], [6, "income"],
                                                                   [7, "latino"], [8, "black"], [9, "asian"],
                                                                   [10, "married"]]}, "variables": {
                "X": {"binary": False, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                      "description": "", "variableName": "X"},
                "age": {"binary": False, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                        "description": "", "variableName": "age"},
                "sex": {"binary": True, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                        "description": "", "variableName": "sex"},
                "educ": {"binary": False, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                         "description": "", "variableName": "educ"},
                "puma": {"binary": False, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                         "description": "", "variableName": "puma"},
                "asian": {"binary": True, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                          "description": "", "variableName": "asian"},
                "black": {"binary": True, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                          "description": "", "variableName": "black"},
                "state": {"binary": False, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                          "description": "", "variableName": "state"},
                "income": {"binary": False, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                           "description": "", "variableName": "income"},
                "latino": {"binary": True, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                           "description": "", "variableName": "latino"},
                "married": {"binary": True, "nature": "ordinal", "numchar": "numeric", "interval": "discrete",
                            "description": "", "variableName": "married"}}}

        # Hack 2: Update to the PUMS data profile_variables
        dataset_info.profile_variables = {"dataset":
                                              {"rowCount": 10000,
                                               "variableCount": 11,
                                               "variableOrder": [[0, "X"], [1, "state"], [2, "puma"], [3, "sex"],
                                                                 [4, "age"], [5, "educ"], [6, "income"], [7, "latino"],
                                                                 [8, "black"], [9, "asian"], [10, "married"]]},
                                          "variables": {"X": {"max": None, "min": None, "name": "X",
                                                              "type": "Numerical", "label": ""},
                                                        "age": {"max": None, "min": None, "name": "age",
                                                                "type": "Numerical", "label": ""},
                                                        "sex": {"name": "sex", "type": "Boolean", "label": ""},
                                                        "educ": {"max": None, "min": None, "name": "educ",
                                                                 "type": "Numerical", "label": ""},
                                                        "puma": {"max": None, "min": None, "name": "puma",
                                                                 "type": "Numerical", "label": ""},
                                                        "asian": {"name": "asian", "type": "Boolean", "label": ""},
                                                        "black": {"name": "black", "type": "Boolean", "label": ""},
                                                        "state": {"max": None, "min": None, "name": "state",
                                                                  "type": "Numerical", "label": ""},
                                                        "income": {"max": None, "min": None, "name": "income",
                                                                   "type": "Numerical", "label": ""},
                                                        "latino": {"name": "latino", "type": "Boolean", "label": ""},
                                                        "married": {"name": "married", "type": "Boolean", "label": ""}}}

        self.add_source_file(dataset_info, 'PUMS5extract10000.csv', True)

        # from django.core import serializers
        # data = serializers.serialize("json", DataSetInfo.objects.filter(pk=4))
        # print('data', data)
        # return

        analysis_plan = self.analysis_plan

        # Hack 3: Update to the PUMS data variable_info
        analysis_plan.variable_info = {"x": {"max": None, "min": None, "name": "X", "type": "Numerical", "label": ""},
                                       "age": {"max": 100, "min": 0, "name": "age", "type": "Numerical",
                                               "label": "age"}, "sex": {"name": "sex", "type": "Boolean", "label": ""},
                                       "educ": {"max": None, "min": None, "name": "educ", "type": "Numerical",
                                                "label": ""},
                                       "puma": {"max": None, "min": None, "name": "puma", "type": "Numerical",
                                                "label": ""},
                                       "asian": {"name": "asian", "type": "Boolean", "label": ""},
                                       "black": {"name": "black", "type": "Boolean", "label": ""},
                                       "state": {"max": None, "min": None, "name": "state", "type": "Numerical",
                                                 "label": ""},
                                       "income": {"max": 100016, "min": 0, "name": "income", "type": "Numerical",
                                                  "label": "income"},
                                       "latino": {"name": "latino", "type": "Boolean", "label": ""},
                                       "married": {"name": "married", "type": "Boolean", "label": ""}}

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = [{'variable': 'age',
                                        'col_index': 4,
                                        'statistic': astatic.DP_SUM,
                                        'dataset_size': 10_000,
                                        'epsilon': 1.0,
                                        'delta': 0.0,
                                        'cl': astatic.CL_95,
                                        'missing_values_handling': astatic.MISSING_VAL_INSERT_FIXED,
                                        'fixed_value': '44',
                                        'variable_info': {'min': 18,
                                                          'max': 95,
                                                          'type': pstatic.VAR_TYPE_INTEGER},
                                        }]

        analysis_plan.save()

        params = dict(object_id=str(analysis_plan.object_id))
        response = self.client.post('/api/release/',
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(jresp['dp_release'])
        self.assertIsNotNone(jresp['object_id'])
        self.assertIsNotNone(jresp['dp_release']['differentially_private_library'])
        self.assertIsNotNone(jresp['dp_release']['statistics'])

        dp_sum_stat = jresp['dp_release']['statistics'][0]

        self.assertEqual(dp_sum_stat['statistic'], astatic.DP_SUM)
        self.assertEqual(dp_sum_stat['variable'], 'age')
        self.assertIsNotNone(dp_sum_stat['result'])
        self.assertIsNotNone(dp_sum_stat['result']['value'])
        self.assertGreater(dp_sum_stat['result']['value'], 400_000)

        # The source_file should be deleted
        self.assertTrue(not analysis_plan.dataset.source_file)

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True, SKIP_EMAIL_RELEASE_FOR_TESTS=False)
    def test_100_release_email(self):
        """(100) Run stats and test email"""
        msgt(self.test_100_release_email.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = self.general_stat_specs
        analysis_plan.save()

        # Check the basics
        #
        release_util = ValidateReleaseUtil.compute_mode( \
            self.user_obj,
            analysis_plan.object_id,
            run_dataverse_deposit=False)

        if release_util.has_error():
            print('release_util:', release_util.get_err_msg())
        self.assertFalse(release_util.has_error())

        release_info_object = release_util.get_new_release_info_object()
        dp_release = release_info_object.dp_release

        stats_list = dp_release['statistics']

        self.assertEqual(len(stats_list), 3)

        # Check the email record
        email_rec = ReleaseEmailRecord.objects.first()
        # print('email_rec.email_content', email_rec.email_content)
        self.assertTrue(email_rec.success)
        self.assertTrue(email_rec.email_content.find(f'Dear {self.user_obj.username}') > -1)
        # self.assertTrue(email_rec.pdf_attached)
        self.assertTrue(email_rec.json_attached)
        self.assertEqual(email_rec.note, '')

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        # Verify that the subject of the first message is correct.
        self.assertTrue(mail.outbox[0].subject.startswith('DP Release ready'))
