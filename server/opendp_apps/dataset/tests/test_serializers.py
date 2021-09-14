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
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.utils.extra_validators import \
    (VALIDATE_MSG_EPSILON,)



class TestReleaseInfoSerializer(TestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):
        # test client
        self.client = APIClient()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        self.client.force_login(self.user_obj)

        self.request = {
            "analysis_plan_id": "98f5ec0d-33ae-45e2-af0e-125276376ef2",
            "dp_statistics": [
                {
                    "statistic": astatic.DP_MEAN,
                    "variable": "BlinkDuration",
                    "epsilon": 1.0,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"
                }
            ]
        }

    def retrieve_new_plan(self):
        """Convenience method to create a new plan"""

        # Create a plan
        #
        dataset_info = DataSetInfo.objects.get(id=4)

        plan_info = AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        self.assertTrue(plan_info.success)
        orig_plan = plan_info.data

        # Retrieve it
        #
        analysis_plan = AnalysisPlan.objects.first()
        self.assertEqual(orig_plan.object_id, analysis_plan.object_id)

        return analysis_plan

    def add_source_file(self, dataset_info: DataSetInfo, filename: str, add_profile: bool=False) -> DataSetInfo:
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
                print(f'!! error: {profiler.get_err_msg()}')

            self.assertTrue(profile_handler.has_error() is False)

        # re-retrieve it...
        return DataSetInfo.objects.get(object_id=dataset_info.object_id)



    def test_10_validate_stats(self):
        """(10) Test a working stat"""
        msgt(self.test_10_validate_stats.__doc__)

        analysis_plan = self.retrieve_new_plan()

        # Send the dp_statistics for validation
        #
        stat_spec =  { \
                "statistic": astatic.DP_MEAN,
                "variable": "EyeHeight",
                "epsilon": 1,
                "delta": 0,
                "error": "",
                "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                "handle_as_fixed": False,
                "fixed_value": "5.0",
                "locked": False,
                "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_info = serializer.save(**dict(opendp_user=self.user_obj))
        print('stats_info.success', stats_info.success)
        self.assertTrue(stats_info.success)

        expected_result = [{'var_name': 'EyeHeight', 'statistic': astatic.DP_MEAN,
                            'valid': True, 'message': None}]
        print('stats_info.data', stats_info.data)
        self.assertEqual(expected_result, stats_info.data)

    def test_15_api_validate_stats(self):
        """(15) Test a working stat via API"""
        msgt(self.test_15_api_validate_stats.__doc__)

        analysis_plan = self.retrieve_new_plan()

        # Send the dp_statistics for validation
        #
        stat_spec = { \
            "statistic": astatic.DP_MEAN,
            "variable": "EyeHeight",
            "epsilon": 1,
            "delta": 0,
            "error": "",
            "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
            "handle_as_fixed": False,
            "fixed_value": "5.0",
            "locked": False,
            "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=[stat_spec])

        response = self.client.post('/api/release/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 200)

        self.assertTrue(jresp['success'])

    def test_20_fail_unsupported_stat(self):
        """(20) Fail: Test a known but unsupported statistic"""
        msgt(self.test_20_fail_unsupported_stat.__doc__)

        analysis_plan = self.retrieve_new_plan()

        # Send the dp_statistics for validation
        #
        stat_spec =  { \
                    "statistic": astatic.DP_SUM,
                    "variable": "EyeHeight",
                    "epsilon": 1,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_info = serializer.save(**dict(opendp_user=self.user_obj))
        print('stats_info.success', stats_info.success)
        self.assertTrue(stats_info.success)

        print('stats_info.data', stats_info.data)
        expected_result = [ \
                {'var_name': 'EyeHeight', 'statistic': astatic.DP_SUM, 'valid': False,
                  'message': 'Statistic "sum" will be supported soon!'}]

        self.assertEqual(expected_result, stats_info.data)


    def test_25_api_fail_unsupported_stat(self):
        """(25) Fail: API, Test a known but unsupported statistic"""
        msgt(self.test_25_api_fail_unsupported_stat.__doc__)

        analysis_plan = self.retrieve_new_plan()

        # Send the dp_statistics for validation
        #
        stat_spec =  { \
                    "statistic": astatic.DP_SUM,
                    "variable": "EyeHeight",
                    "epsilon": 1,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=[stat_spec])

        response = self.client.post('/api/release/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 200)

        self.assertTrue(jresp['success'])

        expected_result = [ \
                {'var_name': 'EyeHeight', 'statistic': astatic.DP_SUM, 'valid': False,
                  'message': 'Statistic "sum" will be supported soon!'}]

        self.assertEqual(expected_result, jresp['data'])


    def test_30_fail_bad_min_max(self):
        """(30) Fail: Add bad min/max values"""
        msgt(self.test_30_fail_bad_min_max.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_info_mod = analysis_plan.variable_info
        # invalid min/max
        variable_info_mod['TypingSpeed']['min'] = 120
        variable_info_mod['TypingSpeed']['max'] = 5
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_spec =  { \
                        "statistic": astatic.DP_MEAN,
                        "variable": "TypingSpeed",
                        "epsilon": 1,
                        "delta": 0,
                        "error": "",
                        "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                        "handle_as_fixed": False,
                        "fixed_value": "5.0",
                        "locked": False,
                        "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        print('stats_valid.success', stats_valid.success)
        self.assertTrue(stats_valid.success)


        expected_result = [ {'var_name': 'TypingSpeed', 'statistic': astatic.DP_MEAN,
                             'valid': False,
                             'message': 'lower bound may not be greater than upper bound'}]
        self.assertEqual(expected_result, stats_valid.data)


    def test_35_api_fail_bad_min_max(self):
        """(35) Fail: API, Add bad min/max values"""
        msgt(self.test_35_api_fail_bad_min_max.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_info_mod = analysis_plan.variable_info
        # invalid min/max
        variable_info_mod['TypingSpeed']['min'] = 120
        variable_info_mod['TypingSpeed']['max'] = 5
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_spec =  { \
                        "statistic": astatic.DP_MEAN,
                        "variable": "TypingSpeed",
                        "epsilon": 1,
                        "delta": 0,
                        "error": "",
                        "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                        "handle_as_fixed": False,
                        "fixed_value": "5.0",
                        "locked": False,
                        "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=[stat_spec])

        response = self.client.post('/api/release/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(jresp['success'])

        expected_result = [{'var_name': 'TypingSpeed', 'statistic': astatic.DP_MEAN,
                            'valid': False,
                            'message': 'lower bound may not be greater than upper bound'}]

        self.assertEqual(expected_result, jresp['data'])
       

    def test_40_fail_single_stat_bad_epsilon(self):
        """(40) Fail: Single stat exceeds total epsilon"""
        msgt(self.test_40_fail_single_stat_bad_epsilon.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_info_mod = analysis_plan.variable_info
        # valid min/max
        variable_info_mod['BlinkDuration']['min'] = 1
        variable_info_mod['BlinkDuration']['max'] = 400
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_spec =  { \
                    "statistic": astatic.DP_MEAN,
                    "variable": "BlinkDuration",
                    "epsilon": 1.5,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        self.assertTrue(stats_valid.success)

        expected_result =  [{'var_name': 'BlinkDuration', 'statistic': astatic.DP_MEAN,
                             'valid': False,
                             'message': VALIDATE_MSG_EPSILON}]

        self.assertEqual(expected_result, stats_valid.data)


    def test_45_api_fail_single_stat_bad_epsilon(self):
        """(45) Fail: API, Single stat exceeds total epsilon"""
        msgt(self.test_45_api_fail_single_stat_bad_epsilon.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_info_mod = analysis_plan.variable_info
        # valid min/max
        variable_info_mod['BlinkDuration']['min'] = 1
        variable_info_mod['BlinkDuration']['max'] = 400
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_spec =  { \
                    "statistic": astatic.DP_MEAN,
                    "variable": "BlinkDuration",
                    "epsilon": 1.5,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        response = self.client.post('/api/release/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(jresp['success'])

        expected_result =  [{'var_name': 'BlinkDuration', 'statistic': astatic.DP_MEAN,
                             'valid': False,
                             'message': VALIDATE_MSG_EPSILON}]

        self.assertEqual(expected_result, jresp['data'])


    def test_50_bad_total_epsilon(self):
        """(50) Fail: Bad total epsilon"""
        msgt(self.test_50_bad_total_epsilon.__doc__)

        analysis_plan = self.retrieve_new_plan()

        setup_info = analysis_plan.dataset.get_depositor_setup_info()
        setup_info.epsilon = 4
        setup_info.save()

        # Send the dp_statistics for validation
        #
        stat_spec = { \
            "statistic": astatic.DP_MEAN,
            "variable": "EyeHeight",
            "epsilon": 1,
            "delta": 0,
            "error": "",
            "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
            "handle_as_fixed": False,
            "fixed_value": "5.0",
            "locked": False,
            "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        self.assertFalse(stats_valid.success)

        self.assertTrue(stats_valid.message.find(astatic.ERR_MSG_BAD_TOTAL_EPSILON) > -1)



    def test_55_api_bad_total_epsilon(self):
        """(50) Fail: API, Bad total epsilon"""
        msgt(self.test_55_api_bad_total_epsilon.__doc__)

        analysis_plan = self.retrieve_new_plan()

        setup_info = analysis_plan.dataset.get_depositor_setup_info()
        setup_info.epsilon = 4
        setup_info.save()

        # Send the dp_statistics for validation
        #
        stat_spec = { \
            "statistic": astatic.DP_MEAN,
            "variable": "EyeHeight",
            "epsilon": 1,
            "delta": 0,
            "error": "",
            "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
            "handle_as_fixed": False,
            "fixed_value": "5.0",
            "locked": False,
            "label": "EyeHeight"}

        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=[stat_spec])

        response = self.client.post('/api/release/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(jresp['success'])

        self.assertTrue(jresp['message'].find(astatic.ERR_MSG_BAD_TOTAL_EPSILON) > -1)

    def test_60_bad_running_epsilon(self):
        """(60) Fail: Total epsilon from dp_statistics > depositor_setup_info.epsilon"""
        msgt(self.test_60_bad_running_epsilon.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_info_mod = analysis_plan.variable_info
        # valid min/max
        variable_info_mod['EyeHeight']['min'] = 0.2
        variable_info_mod['EyeHeight']['max'] = 4.1

        variable_info_mod['BlinkDuration']['min'] = 1
        variable_info_mod['BlinkDuration']['max'] = 400
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_specs = [\
                { \
                    "statistic": astatic.DP_MEAN,
                    "variable": "EyeHeight",
                    "epsilon": 0.6,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight",
                },
                { \
                    "statistic": astatic.DP_MEAN,
                    "variable": "BlinkDuration",
                    "epsilon": 0.45,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "BlinkDuration",
                }]

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=stat_specs)

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        self.assertTrue(stats_valid.success)

        sample_result_data = [{'var_name': 'EyeHeight', 'statistic': 'mean', 'valid': False,
                            'message': 'constant must be a member of DA'},
                           {'var_name': 'BlinkDuration', 'statistic': 'mean', 'valid': False,
                            'message': 'The running epsilon (1.05) exceeds the max epsilon (1.0)'}]

        self.assertTrue(stats_valid.data[0]['valid'] is False)
        self.assertTrue(stats_valid.data[1]['valid'] is False)
        self.assertTrue(stats_valid.data[1]['message'].find('exceeds the max epsilon') > -1)

    def test_65_bad_running_epsilon(self):
        """(65) Fail: API,  Total epsilon from dp_statistics > depositor_setup_info.epsilon"""
        msgt(self.test_65_bad_running_epsilon.__doc__)

        analysis_plan = self.retrieve_new_plan()

        variable_info_mod = analysis_plan.variable_info
        # valid min/max
        variable_info_mod['EyeHeight']['min'] = 0.2
        variable_info_mod['EyeHeight']['max'] = 4.1

        variable_info_mod['BlinkDuration']['min'] = 1
        variable_info_mod['BlinkDuration']['max'] = 400
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_specs = [ \
            { \
                "statistic": astatic.DP_MEAN,
                "variable": "EyeHeight",
                "epsilon": 0.6,
                "delta": 0,
                "error": "",
                "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                "handle_as_fixed": False,
                "fixed_value": "5.0",
                "locked": False,
                "label": "EyeHeight",
            },
            { \
                "statistic": astatic.DP_MEAN,
                "variable": "BlinkDuration",
                "epsilon": 0.45,
                "delta": 0,
                "error": "",
                "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                "handle_as_fixed": False,
                "fixed_value": "5.0",
                "locked": False,
                "label": "BlinkDuration",
            }]

        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=stat_specs)

        response = self.client.post('/api/release/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 200)

        sample_result_data = [{'var_name': 'EyeHeight', 'statistic': 'mean', 'valid': False,
                               'message': 'constant must be a member of DA'},
                              {'var_name': 'BlinkDuration', 'statistic': 'mean', 'valid': False,
                               'message': 'The running epsilon (1.05) exceeds the max epsilon (1.0)'}]

        self.assertTrue(jresp['data'][0]['valid'] is False)
        self.assertTrue(jresp['data'][1]['valid'] is False)
        self.assertTrue(jresp['data'][1]['message'].find('exceeds the max epsilon') > -1)

    @skip
    def test_70_show_add_file(self):
        """(70) Sample of attaching file to a DataSetInfo object"""
        msgt(self.test_70_show_add_file.__doc__)

        analysis_plan = self.retrieve_new_plan()

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


"""

           
            {'var_name': 'TypingSpeed', 'statistic': 'mean', 'valid': False,
             'message': 'lower bound may not be greater than upper bound'}]
   
     # Set bad min/max for a variable
        #
        variable_info_mod = analysis_plan.variable_info
        # invalid min/max
        variable_info_mod['TypingSpeed']['min'] = 120
        variable_info_mod['TypingSpeed']['max'] = 5
        # valid min/max
        variable_info_mod['BlinkDuration']['min'] = 1
        variable_info_mod['BlinkDuration']['max'] = 400
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()          
"""