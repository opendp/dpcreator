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
                            "ci": astatic.CI_95,
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
            print('profile_handler.has_error()', profile_handler.has_error())

            # Shouldn't have errors
            if profile_handler.has_error():
                print(f'!! error: {profile_handler.get_err_msg()}')

            self.assertTrue(profile_handler.has_error() is False)

        # re-retrieve it...
        return DataSetInfo.objects.get(object_id=dataset_info.object_id)



    def test_10_validate_stats(self):
        """(10) Test a working stat"""
        msgt(self.test_10_validate_stats.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        dp_statistics = self.general_stat_specs

        # Check the basics
        #
        release_util = ValidateReleaseUtil(self.user_obj,
                                           analysis_plan.object_id,
                                           dp_statistics)
        # release_util.run_validation_process()
        release_util.run_release_process()

        self.assertFalse(release_util.has_error())

        release_list = release_util.get_release_stats()

        self.assertEqual(release_list[0]['variable'], 'EyeHeight')
        self.assertTrue('result' in release_list[0])
        self.assertTrue('value' in release_list[0]['result'])
        self.assertTrue(float(release_list[0]['result']['value']))

        self.assertEqual(release_list[1]['variable'], 'TypingSpeed')
        self.assertTrue('result' in release_list[1])
        self.assertTrue('value' in release_list[1]['result'])
        self.assertTrue(float(release_list[1]['result']['value']))


    @skip
    def test_15_api_validate_stats(self):
        """(15) Test a working stat via API"""
        msgt(self.test_15_api_validate_stats.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        stat_spec = self.general_stat_spec

        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=[stat_spec])

        response = self.client.post('/api/validation/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 200)

        self.assertTrue(jresp['success'])


    @skip
    def test_70_show_add_file(self):
        """(70) Sample of attaching file to a DataSetInfo object"""
        msgt(self.test_70_show_add_file.__doc__)

        analysis_plan = self.analysis_plan

        dataset_info_1 = analysis_plan.dataset
        dataset_info_1.data_profile = None
        dataset_info_1.profile_variables = None
        dataset_info_1.save()

        dataset_info_updated = self.add_source_file(analysis_plan.dataset, 'Fatigue_data.tab', True)

        self.assertTrue('variables' in dataset_info_updated.data_profile)
        self.assertTrue('dataset' in dataset_info_updated.data_profile)

        self.assertTrue('variables' in dataset_info_updated.profile_variables)
        self.assertTrue('dataset' in dataset_info_updated.profile_variables)

        # print(json.dumps(dataset_info_2.data_profile, indent=4))
        # print(json.dumps(dataset_info_2.profile_variables, indent=4))

