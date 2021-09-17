from os.path import abspath, dirname, isdir, isfile, join

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')
from unittest import skip

import json
from django.contrib.auth import get_user_model
from django.core.files import File
from django.test.testcases import TestCase

from rest_framework.test import APIClient

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.serializers import ReleaseValidationSerializer
from opendp_apps.analysis.validate_release_util import ValidateReleaseUtil
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.utils.extra_validators import VALIDATE_MSG_EPSILON


class TestRunRelease(TestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):
        # test client
        self.client = APIClient()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        self.client.force_login(self.user_obj)

        dataset_info = DataSetInfo.objects.get(id=4)
        self.add_source_file(dataset_info, 'Fatigue_data.tab', True)

        plan_info = AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        self.assertTrue(plan_info.success)
        orig_plan = plan_info.data

        # Retrieve it
        #
        self.analysis_plan = AnalysisPlan.objects.first()
        self.assertEqual(orig_plan.object_id, self.analysis_plan.object_id)

        self.analysis_plan.variable_info['EyeHeight']['min'] = -8.01
        self.analysis_plan.variable_info['EyeHeight']['max'] = 5

        self.analysis_plan.variable_info['TypingSpeed']['min'] = 3
        self.analysis_plan.variable_info['TypingSpeed']['max'] = 30

        #analysis_plan.variable_info = variable_info_mod
        self.analysis_plan.save()

        self.general_stat_specs = [\
                            {"statistic": astatic.DP_MEAN,
                              "variable": "EyeHeight",
                              "epsilon": .45,
                              "delta": 0,
                              "ci": astatic.CI_95,
                              "error": "",
                              "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                              "handle_as_fixed": False,
                              "fixed_value": "1",
                              "locked": False,
                              "label": "EyeHeight"
                              },
                           {"statistic": astatic.DP_MEAN,
                            "variable": "TypingSpeed",
                            "epsilon": .5,
                            "delta": 0,
                            "ci": astatic.CI_99,
                            "error": "",
                            "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                            "handle_as_fixed": False,
                            "fixed_value": "9",
                            "locked": False,
                            "label": "TypingSpeed"
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



    def test_10_compute_stats(self):
        """(10) Run compute stats"""
        msgt(self.test_10_compute_stats.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        analysis_plan.dp_statistics = self.general_stat_specs
        analysis_plan.save()

        # Check the basics
        #
        release_util = ValidateReleaseUtil.compute_mode(\
                               self.user_obj,
                               analysis_plan.object_id)

        self.assertFalse(release_util.has_error())

        release_info_object = release_util.get_new_release_info_object()
        dp_release = release_info_object.dp_release
        release_list = dp_release['statistics']

        self.assertEqual(release_list[0]['variable'], 'EyeHeight')
        self.assertTrue('result' in release_list[0])
        self.assertTrue('value' in release_list[0]['result'])
        self.assertTrue(float(release_list[0]['result']['value']))

        self.assertEqual(release_list[1]['variable'], 'TypingSpeed')
        self.assertTrue('result' in release_list[1])
        self.assertTrue('value' in release_list[1]['result'])
        self.assertTrue(float(release_list[1]['result']['value']))


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
        setup_info.epsilon = None   # Shouldn't happen but what if it does!
        setup_info.save()

        params = dict(object_id=str(analysis_plan.object_id))
        response = self.client.post('/api/release/',
                                    json.dumps(params),
                                    content_type='application/json')

        jresp = response.json()
        print('jresp', jresp)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(jresp['success'])
        self.assertTrue(jresp['message'].find(astatic.ERR_MSG_BAD_TOTAL_EPSILON) > -1)


    def test_50_success(self):
        """(50) Via API, run compute stats with error"""
        msgt(self.test_50_success.__doc__)

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
        print('jresp', jresp)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(jresp['dp_release'])
        self.assertIsNotNone(jresp['object_id'])


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
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(jresp['dp_release'])
        self.assertIsNotNone(jresp['object_id'])

        response = self.client.get(f'/api/analyze/{analysis_plan.object_id}/')
        analysis_plan_jresp = response.json()
        # from pprint import pprint
        # pprint(analysis_plan_jresp)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(analysis_plan_jresp['release_info'])

