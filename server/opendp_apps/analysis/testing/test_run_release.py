import json
from os.path import abspath, dirname, isfile, join

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files import File
from django.test import override_settings
from rest_framework import status
from rest_framework.reverse import reverse as drf_reverse
from rest_framework.test import APIClient

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.models import AnalysisPlan, ReleaseEmailRecord
from opendp_apps.analysis.release_info_formatter import ReleaseInfoFormatter
from opendp_apps.analysis.testing.base_stat_spec_test import StatSpecTestCase
from opendp_apps.analysis.validate_release_util import ValidateReleaseUtil
from opendp_apps.dataset.dataset_formatter import DatasetFormatter
from opendp_apps.dataset.depositor_setup_helpers import get_selected_variable_info
from opendp_apps.dataset.models import DatasetInfo
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.utils.extra_validators import VALIDATE_MSG_EPSILON

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class TestRunRelease(StatSpecTestCase):

    def setUp(self):
        super().setUp()

        # test client
        self.client = APIClient()

        # self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        self.client.force_login(self.user_obj)

        # dataset_info = DatasetInfo.objects.get(id=4)
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

    def add_source_file(self, dataset_info: DatasetInfo, filename: str, add_profile: bool = False) -> DatasetInfo:
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
        return DatasetInfo.objects.get(object_id=dataset_info.object_id)

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_010_compute_stats(self):
        """(10) Run compute stats"""
        msgt(self.test_010_compute_stats.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = [self.general_stat_specs[2]]
        analysis_plan.save()

        analysis_plan2 = AnalysisPlan.objects.get(object_id=analysis_plan.object_id)
        # print('analysis_plan.dp_statistics - after save', analysis_plan2.dp_statistics)

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

    def test_030_api_bad_stat(self):
        """(30) Via API, run compute stats with error"""
        msgt(self.test_030_api_bad_stat.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        self.general_stat_specs[0]['epsilon'] = 3.2
        analysis_plan.dp_statistics = self.general_stat_specs
        analysis_plan.save()

        params = dict(object_id=str(analysis_plan.object_id))
        response = self.client.post(self.API_RELEASE_PREFIX,
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        # print('jresp', jresp)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(jresp['success'])
        self.assertTrue(jresp['message'].find(VALIDATE_MSG_EPSILON) > -1)

    # @skip('Reconfiguring for analyst mode')
    def test_040_api_bad_overall_epsilon(self):
        """(40) Via API, run compute stats, bad overall epsilon"""
        msgt(self.test_040_api_bad_overall_epsilon.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = self.general_stat_specs

        # Put some bad data in!
        analysis_plan.epsilon = None  # Shouldn't happen but what if it does!
        analysis_plan.save()

        params = dict(object_id=str(analysis_plan.object_id))
        response = self.client.post(self.API_RELEASE_PREFIX,
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        print('jresp', jresp)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(jresp['success'])
        self.assertTrue(jresp['message'].find(astatic.ERR_MSG_BAD_EPSILON_ANALYSIS_PLAN.format(epsilon=None)) > -1)

    # @skip('Reconfiguring for analyst mode')
    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_050_success(self):
        """(50) Via API, run compute stats successfully"""
        msgt(self.test_050_success.__doc__)

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

        response = self.client.post(self.API_RELEASE_PREFIX,
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
        # - Not applicable in that this is a direct file upload
        # self.assertTrue(AuxiliaryFileDepositRecord.objects.filter(release_info=updated_plan.release_info).count() > 0)
        # for dep_rec in AuxiliaryFileDepositRecord.objects.filter(release_info=updated_plan.release_info):
        #    self.assertTrue(dep_rec.deposit_success is False)
        #    self.assertTrue(dep_rec.http_status_code == 403 or \
        #                    dep_rec.http_status_code < 0)

        # The source_file should be deleted
        # analysis_plan = AnalysisPlan.objects.get(id=analysis_plan.id)
        # self.assertTrue(not analysis_plan.dataset.source_file)

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_055_success_download_urls(self):
        """(55) Test PDF and JSOn download Urls"""
        msgt(self.test_055_success_download_urls.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = self.general_stat_specs
        analysis_plan.save()

        params = dict(object_id=str(analysis_plan.object_id))

        response = self.client.post(self.API_RELEASE_PREFIX,
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        # print('jresp', jresp)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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

        # The source_file should be deleted, no longer true
        # self.assertTrue(not analysis_plan.dataset.source_file)

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_060_analysis_plan_has_release_info(self):
        """(60) Via API, ensure that release_info is added as a field to AnalysisPlan"""
        msgt(self.test_060_analysis_plan_has_release_info.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = self.general_stat_specs
        analysis_plan.save()

        params = dict(object_id=str(analysis_plan.object_id))
        response = self.client.post(self.API_RELEASE_PREFIX,
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(jresp['dp_release'])
        self.assertIsNotNone(jresp['object_id'])

        response = self.client.get(f'/api/analysis-plan/{analysis_plan.object_id}/')
        analysis_plan_jresp = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
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
        # - Not applicable in that this is a direct file upload
        """
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
        """

    def test_070_dataset_formatter_eye_fatigue_file(self):
        """(70) Test the DatasetFormatter -- dataset info formatted for inclusion in ReleaseInfo.dp_release"""
        msgt(self.test_070_dataset_formatter_eye_fatigue_file.__doc__)
        """
        Expected result:
        {
            "type": "upload",
            "name": "Replication Data for: Eye-typing experiment",
            "fileFormat": "(unknown file type)",
            "creator": {
                "first_name": "Kenny",
                "last_name": "Powers",
                "email": "kpowers@ridiculous.edu"
            },
            "upload_date": {
                "iso": "2023-08-04T19:45:42.237148+00:00",
                "human_readable": "August 4, 2023 at 19:45:42:237148 UTC",
                "human_readable_date_only": "4 August, 2023"
            }
        }
        """
        formatter = DatasetFormatter(self.analysis_plan.dataset)
        if formatter.has_error():
            print(formatter.get_err_msg())

        self.assertFalse(formatter.has_error())
        ds_info = formatter.get_formatted_info()
        # print(json.dumps(ds_info, indent=4))

        self.assertEqual(ds_info['type'], "upload")
        self.assertEqual(ds_info['name'], "Replication Data for: Eye-typing experiment")

        self.assertEqual(ds_info['creator']['first_name'], "Kenny")
        self.assertTrue('iso' in ds_info['upload_date'])
        self.assertTrue('human_readable' in ds_info['upload_date'])

    @override_settings(SKIP_PDF_CREATION_FOR_TESTS=True)
    def test_090_dp_count_pums_data(self):
        """
        (90) Via API, Test DP Count with PUMS data.
        Note: This is very hack! A full DatasetInfo object with related objects should be saved as a separate fixture
        """
        msgt(self.test_090_dp_count_pums_data.__doc__)

        dataset_info = DatasetInfo.objects.get(id=self.eye_typing_dataset.id)

        # Hack 1: Update to the PUMS data profile_variables
        dataset_info.depositor_setup_info.data_profile = {"dataset":
                                                              {"rowCount": 10000,
                                                               "variableCount": 11,
                                                               "variableOrder": [[0, "X"], [1, "state"], [2, "puma"],
                                                                                 [3, "sex"],
                                                                                 [4, "age"], [5, "educ"], [6, "income"],
                                                                                 [7, "latino"],
                                                                                 [8, "black"], [9, "asian"],
                                                                                 [10, "married"]]},
                                                          "variables": {"X": {"max": None, "min": None, "name": "X",
                                                                              "type": "Numerical", "label": ""},
                                                                        "age": {"max": None, "min": None, "name": "age",
                                                                                "type": "Numerical", "label": ""},
                                                                        "sex": {"name": "sex", "type": "Boolean",
                                                                                "label": ""},
                                                                        "educ": {"max": None, "min": None,
                                                                                 "name": "educ",
                                                                                 "type": "Numerical", "label": ""},
                                                                        "puma": {"max": None, "min": None,
                                                                                 "name": "puma",
                                                                                 "type": "Numerical", "label": ""},
                                                                        "asian": {"name": "asian", "type": "Boolean",
                                                                                  "label": ""},
                                                                        "black": {"name": "black", "type": "Boolean",
                                                                                  "label": ""},
                                                                        "state": {"max": None, "min": None,
                                                                                  "name": "state",
                                                                                  "type": "Numerical", "label": ""},
                                                                        "income": {"max": None, "min": None,
                                                                                   "name": "income",
                                                                                   "type": "Numerical", "label": ""},
                                                                        "latino": {"name": "latino", "type": "Boolean",
                                                                                   "label": ""},
                                                                        "married": {"name": "married",
                                                                                    "type": "Boolean", "label": ""}}}

        self.add_source_file(dataset_info, 'PUMS5extract10000.csv', True)

        dataset_info.depositor_setup_info.variable_info = {
            "age": {"max": 100, "min": 0,
                    "name": "age",
                    "label": "age",
                    "type": "Numerical",
                    "selected": True},
            "income": {"max": 100016, "min": 0,
                       "name": "income",
                       "label": "income",
                       "type": "Numerical",
                       "selected": True},
        }

        dataset_info.depositor_setup_info.save()
        dataset_info.save()

        analysis_plan = self.analysis_plan

        var_info_resp = get_selected_variable_info(dataset_info.depositor_setup_info.variable_info)
        self.assertTrue(var_info_resp.success is True)

        analysis_plan.variable_info = var_info_resp.data

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
        response = self.client.post(self.API_RELEASE_PREFIX,
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        # print('jresp', jresp)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
        # self.assertTrue(not analysis_plan.dataset.source_file)

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

    def test_110_get_release_by_api(self):
        """(110) Get release by API"""
        msgt(self.test_110_get_release_by_api.__doc__)

        release_info_obj = self.get_release_info()
        release_info_object_id = str(release_info_obj.object_id)

        release_get_url = f'{self.API_RELEASE_PREFIX}{release_info_object_id}/'

        response = self.client.get(release_get_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['object_id'], release_info_object_id)

    def test_115_get_release_by_api_another_user(self):
        """(115) Get release by API, another user"""
        msgt(self.test_115_get_release_by_api_another_user.__doc__)

        release_info_obj = self.get_release_info()
        release_info_object_id = str(release_info_obj.object_id)

        # Make unauthorized user
        #
        new_user_params = dict(username='jgemstone',
                               email='jgemstone@ridiculous.edu',
                               first_name='Judy',
                               last_name='Gemstone')

        new_user, _created = get_user_model().objects.get_or_create(**new_user_params)
        self.client.force_login(new_user)

        release_get_url = f'{self.API_RELEASE_PREFIX}{release_info_object_id}/'

        response = self.client.get(release_get_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_118_get_release_user_not_logged_in(self):
        """(118) Get release by API, not logged in"""
        msgt(self.test_118_get_release_user_not_logged_in.__doc__)

        release_info_obj = self.get_release_info()
        release_info_object_id = str(release_info_obj.object_id)

        release_get_url = f'{self.API_RELEASE_PREFIX}{release_info_object_id}/'

        self.client = APIClient()

        response = self.client.get(release_get_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_120_fail_to_delete_release_by_api(self):
        """(120) Fail to delete Release by API """
        msgt(self.test_120_fail_to_delete_release_by_api.__doc__)

        release_info_obj = self.get_release_info()
        release_info_object_id = str(release_info_obj.object_id)

        release_del_url = f'{self.API_RELEASE_PREFIX}{release_info_object_id}/'

        response = self.client.delete(release_del_url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_130_fail_to_patch_release_by_api(self):
        """(130) Fail to patch release by API"""
        msgt(self.test_130_fail_to_patch_release_by_api.__doc__)

        release_info_obj = self.get_release_info()
        release_info_object_id = str(release_info_obj.object_id)

        release_patch_url = f'{self.API_RELEASE_PREFIX}{release_info_object_id}/'

        # Patch dp_release
        payload = json.dumps(dict(dp_release=dict(hi='there')))

        response = self.client.patch(release_patch_url,
                                     payload,
                                     content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Patch epsilon
        payload = json.dumps(dict(epsilon=0.75))

        response = self.client.patch(release_patch_url,
                                     payload,
                                     content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_140_fail_to_list_releases_by_api(self):
        """(140) Fail to list releases by API"""
        msgt(self.test_140_fail_to_list_releases_by_api.__doc__)

        _release_info_obj = self.get_release_info()

        response = self.client.get(self.API_RELEASE_PREFIX)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
