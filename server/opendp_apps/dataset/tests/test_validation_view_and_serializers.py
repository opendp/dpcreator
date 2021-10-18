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
from opendp_apps.utils.extra_validators import VALIDATE_MSG_EPSILON



class TestValidationViewAndSerializers(TestCase):
    fixtures = ['test_dataset_data_001.json', ]

    def setUp(self):
        # test client
        self.client = APIClient()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        self.client.force_login(self.user_obj)

        dataset_info = DataSetInfo.objects.get(id=4)

        plan_info = AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        self.assertTrue(plan_info.success)
        orig_plan = plan_info.data

        # Retrieve it
        #
        self.analysis_plan = AnalysisPlan.objects.first()
        self.assertEqual(orig_plan.object_id, self.analysis_plan.object_id)

        self.general_stat_spec = {"statistic": astatic.DP_MEAN,
                "variable": "EyeHeight",
                "epsilon": 1,
                "delta": 0,
                "ci": astatic.CI_95_ALPHA,
                "error": "",
                "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                "handle_as_fixed": False,
                "fixed_value": "5.0",
                "locked": False,
                "label": "EyeHeight"
                }
    

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
                print(f'!! error: {profile_handler.get_err_msg()}')

            self.assertTrue(profile_handler.has_error() is False)

        # re-retrieve it...
        return DataSetInfo.objects.get(object_id=dataset_info.object_id)

    def test_05_api_fail_not_logged_in(self):
        """(5) Test API fail, not logged in"""
        msgt(self.test_05_api_fail_not_logged_in.__doc__)

        client = APIClient()
        dataset_info = DataSetInfo.objects.get(id=4)
        AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        analysis_plan = AnalysisPlan.objects.first()

        # Send the dp_statistics for validation
        #
        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[self.general_stat_spec])

        response = client.post('/api/validation/', data=request_plan, format='json')
        #print('response.status_code', response.status_code)
        #print('json', response.json())
        self.assertEqual(response.status_code, 403)



    def test_08_api_fail_wrong_user(self):
        """(8) Test API fail, logged in as different user"""
        msgt(self.test_08_api_fail_wrong_user.__doc__)

        new_client = APIClient()
        other_user_obj, _created = get_user_model().objects.get_or_create(username='test_user')
        new_client.force_login(other_user_obj)

        dataset_info = DataSetInfo.objects.get(id=4)
        AnalysisPlanUtil.create_plan(dataset_info.object_id, self.user_obj)
        analysis_plan = AnalysisPlan.objects.first()

        # Send the dp_statistics for validation
        #
        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[self.general_stat_spec])

        response = new_client.post('/api/validation/', data=request_plan, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()['success'])
        self.assertEqual(response.json()['message'], astatic.ERR_MSG_NO_ANALYSIS_PLAN)


    def test_10_validate_stats(self):
        """(10) Test a working stat"""
        msgt(self.test_10_validate_stats.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[self.general_stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()
        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_info = serializer.save(**dict(opendp_user=self.user_obj))
        #print('stats_info.success', stats_info.success)
        self.assertTrue(stats_info.success)

        expected_result = [{'variable': 'EyeHeight', 'statistic': 'mean', 'valid': True,
                            'message': None,
                            'accuracy': {
                                'value': 1.6370121873967791,
                                'message': 'Releasing mean for the variable EyeHeight. With at least probability 0.95 the output mean will differ from the true mean by at most 1.6370121873967791 units. Here the units are the same units the variable has in the dataset.'}}]

        #print('stats_info.data', stats_info.data)
        self.assertEqual(stats_info.data[0]['valid'], True)

        # Were accuracy results included?
        self.assertTrue('value' in stats_info.data[0]['accuracy'])
        self.assertTrue('message' in stats_info.data[0]['accuracy'])

        accuracy_msg = f'output {astatic.DP_MEAN} will differ from the true {astatic.DP_MEAN} by at'
        self.assertTrue(stats_info.data[0]['accuracy']['message'].find(accuracy_msg) > -1)


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

    def test_20_fail_unsupported_stat(self):
        """(20) Fail: Test a known but unsupported statistic"""
        msgt(self.test_20_fail_unsupported_stat.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        stat_spec =  self.general_stat_spec
        stat_spec['statistic'] = astatic.DP_QUANTILE

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
        #print('stats_info.success', stats_info.success)
        self.assertTrue(stats_info.success)

        self.assertEqual(stats_info.data[0]['valid'], False)
        self.assertEqual(stats_info.data[0]['statistic'], astatic.DP_QUANTILE)
        self.assertEqual(stats_info.data[0]['variable'], 'EyeHeight')
        self.assertEqual(stats_info.data[0]['message'], f'Statistic "{astatic.DP_QUANTILE}" will be supported soon!')

    def test_25_api_fail_unsupported_stat(self):
        """(25) Fail: API, Test a known but unsupported statistic"""
        msgt(self.test_25_api_fail_unsupported_stat.__doc__)

        analysis_plan = self.analysis_plan

        # Send the dp_statistics for validation
        #
        stat_spec =  self.general_stat_spec
        stat_spec['statistic'] = astatic.DP_QUANTILE


        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=[stat_spec])

        response = self.client.post('/api/validation/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 200)

        self.assertTrue(jresp['success'])

        self.assertEqual(jresp['data'][0]['valid'], False)
        self.assertEqual(jresp['data'][0]['statistic'], astatic.DP_QUANTILE)
        self.assertEqual(jresp['data'][0]['variable'], 'EyeHeight')
        self.assertEqual(jresp['data'][0]['message'], f'Statistic "{astatic.DP_QUANTILE}" will be supported soon!')


    def test_30_fail_bad_min_max(self):
        """(30) Fail: Add bad min/max values"""
        msgt(self.test_30_fail_bad_min_max.__doc__)

        analysis_plan = self.analysis_plan

        variable_info_mod = analysis_plan.variable_info
        # invalid min/max
        variable_info_mod['TypingSpeed']['min'] = 120
        variable_info_mod['TypingSpeed']['max'] = 5
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_spec = self.general_stat_spec
        stat_spec['variable'] = "TypingSpeed"

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
        #print('stats_valid.success', stats_valid.success)
        self.assertTrue(stats_valid.success)


        expected_result = [ {'variable': 'TypingSpeed', 'statistic': astatic.DP_MEAN,
                             'valid': False,
                             'message': astatic.ERR_MSG_INVALID_MIN_MAX}]

        # self.assertEqual(expected_result, stats_valid.data)
        self.assertEqual(stats_valid.data[0]['valid'], False)
        self.assertTrue(stats_valid.data[0]['message'].find('must be less than the max') > -1)


    def test_35_api_fail_bad_min_max(self):
        """(35) Fail: API, Add bad min/max values"""
        msgt(self.test_35_api_fail_bad_min_max.__doc__)

        analysis_plan = self.analysis_plan

        variable_info_mod = analysis_plan.variable_info
        # invalid min/max
        variable_info_mod['TypingSpeed']['min'] = 120
        variable_info_mod['TypingSpeed']['max'] = 5
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_spec = self.general_stat_spec
        stat_spec['variable'] = "TypingSpeed"
        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=[stat_spec])

        response = self.client.post('/api/validation/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(jresp['success'])

        expected_result = [{'variable': 'TypingSpeed', 'statistic': astatic.DP_MEAN,
                            'valid': False,
                            'message': astatic.ERR_MSG_INVALID_MIN_MAX}]

        # self.assertEqual(jresp['data'], expected_result)

        self.assertEqual(jresp['data'][0]['valid'], False)
        self.assertTrue(jresp['data'][0]['message'].find('must be less than the max') > -1)

    def test_40_fail_single_stat_bad_epsilon(self):
        """(40) Fail: Single stat exceeds total epsilon"""
        msgt(self.test_40_fail_single_stat_bad_epsilon.__doc__)

        analysis_plan = self.analysis_plan

        variable_info_mod = analysis_plan.variable_info
        # valid min/max
        variable_info_mod['BlinkDuration']['min'] = 1
        variable_info_mod['BlinkDuration']['max'] = 400
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_spec = self.general_stat_spec
        stat_spec['epsilon'] = 1.5

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
        print('40!! stats_valid', stats_valid.data)
        self.assertEqual(stats_valid.data[0]['valid'], False)
        self.assertTrue(stats_valid.data[0]['message'].find(VALIDATE_MSG_EPSILON) > -1)

    def test_45_api_fail_single_stat_bad_epsilon(self):
        """(45) Fail: API, Single stat exceeds total epsilon"""
        msgt(self.test_45_api_fail_single_stat_bad_epsilon.__doc__)

        analysis_plan = self.analysis_plan

        variable_info_mod = analysis_plan.variable_info
        # valid min/max
        analysis_plan.variable_info['BlinkDuration']['min'] = 1.0
        analysis_plan.variable_info['BlinkDuration']['max'] = 400.0
        #analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_spec = self.general_stat_spec
        stat_spec['epsilon'] = 1.5

        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        valid = serializer.is_valid()

        self.assertTrue(valid)
        self.assertTrue(serializer.errors == {})

        response = self.client.post('/api/validation/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(jresp['success'])

        # print('jresp', jresp)

        self.assertEqual(jresp['data'][0]['valid'], False)
        self.assertTrue(jresp['data'][0]['message'].find(VALIDATE_MSG_EPSILON) > -1)


    def test_50_bad_total_epsilon(self):
        """(50) Fail: Bad total epsilon"""
        msgt(self.test_50_bad_total_epsilon.__doc__)

        analysis_plan = self.analysis_plan

        setup_info = analysis_plan.dataset.get_depositor_setup_info()
        setup_info.epsilon = 4
        setup_info.save()

        # Send the dp_statistics for validation
        #
        stat_spec = self.general_stat_spec

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
        """(55) Fail: API, Bad total epsilon"""
        msgt(self.test_55_api_bad_total_epsilon.__doc__)

        analysis_plan = self.analysis_plan

        setup_info = analysis_plan.dataset.get_depositor_setup_info()
        setup_info.epsilon = 4
        setup_info.save()

        # Send the dp_statistics for validation
        #
        stat_spec = self.general_stat_spec

        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=[stat_spec])

        response = self.client.post('/api/validation/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertFalse(jresp['success'])

        self.assertTrue(jresp['message'].find(astatic.ERR_MSG_BAD_TOTAL_EPSILON) > -1)

    def get_test_60_65_specs(self):
        """Specs"""
        spec1 = self.general_stat_spec
        spec2 = self.general_stat_spec.copy()

        spec1['epsilon'] = 0.6

        spec2["variable"] = "BlinkDuration"
        spec2['epsilon'] = 0.45

        stat_specs = [spec1, spec2]

        return stat_specs

    def test_60_bad_running_epsilon(self):
        """(60) Fail: Total epsilon from dp_statistics > depositor_setup_info.epsilon"""
        msgt(self.test_60_bad_running_epsilon.__doc__)

        analysis_plan = self.analysis_plan

        variable_info_mod = analysis_plan.variable_info

        variable_info_mod['BlinkDuration']['min'] = 1
        variable_info_mod['BlinkDuration']['max'] = 400
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_specs = self.get_test_60_65_specs()

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

        _sample_result_data = [{'variable': 'EyeHeight', 'statistic': 'mean', 'valid': False,
                            'message': 'constant must be a member of DA'},
                           {'variable': 'BlinkDuration', 'statistic': 'mean', 'valid': False,
                            'message': 'The running epsilon (1.05) exceeds the max epsilon (1.0)'}]

        self.assertTrue(stats_valid.data[0]['valid'] is True)
        self.assertTrue(stats_valid.data[1]['valid'] is False)
        self.assertTrue(stats_valid.data[1]['message'].find('exceeds the max epsilon') > -1)

    def test_65_api_bad_running_epsilon(self):
        """(65) Fail: API,  Total epsilon from dp_statistics > depositor_setup_info.epsilon"""
        msgt(self.test_65_api_bad_running_epsilon.__doc__)

        analysis_plan = self.analysis_plan

        variable_info_mod = analysis_plan.variable_info

        variable_info_mod['BlinkDuration']['min'] = 1
        variable_info_mod['BlinkDuration']['max'] = 400
        analysis_plan.variable_info = variable_info_mod
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_specs = self.get_test_60_65_specs()

        request_plan = dict(analysis_plan_id=str(analysis_plan.object_id),
                            dp_statistics=stat_specs)
        response = self.client.post('/api/validation/',
                                    json.dumps(request_plan),
                                    content_type='application/json')

        jresp = response.json()
        self.assertEqual(response.status_code, 200)
        # print(json.dumps(jresp, indent=4))

        _sample_result_data = [{'variable': 'EyeHeight', 'statistic': 'mean', 'valid': False,
                               'message': 'constant must be a member of DA'},
                              {'variable': 'BlinkDuration', 'statistic': 'mean', 'valid': False,
                               'message': 'The running epsilon (1.05) exceeds the max epsilon (1.0)'}]

        self.assertTrue(jresp['data'][0]['valid'] is True)
        self.assertTrue(jresp['data'][1]['valid'] is False)
        self.assertTrue(jresp['data'][1]['message'].find('exceeds the max epsilon') > -1)


    def test_70_fail_impute_too_high(self):
        """(70) Fail: Impute higher than max"""
        msgt(self.test_70_fail_impute_too_high.__doc__)

        analysis_plan = self.analysis_plan

        # invalid min/max
        analysis_plan.variable_info['EyeHeight']['min'] = -8
        analysis_plan.variable_info['EyeHeight']['max'] = 5
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_spec = self.general_stat_spec
        stat_spec['fixed_value'] = 40

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        self.assertTrue(serializer.is_valid())

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        print('stats_valid.data', stats_valid.data)
        self.assertTrue(stats_valid.success)
        self.assertFalse(stats_valid.data[0]['valid'])

        user_msg2 = 'The "fixed value" (40.0) cannot be more than the "max" (5.0)'
        self.assertEqual(stats_valid.data[0]['message'], user_msg2)


    def test_80_fail_impute_too_low(self):
        """(80) Fail: Impute lower than min"""
        msgt(self.test_80_fail_impute_too_low.__doc__)

        analysis_plan = self.analysis_plan

        # invalid min/max
        analysis_plan.variable_info['EyeHeight']['min'] = -8
        analysis_plan.variable_info['EyeHeight']['max'] = 5
        analysis_plan.save()


        # Send the dp_statistics for validation
        #
        # Send the dp_statistics for validation
        #
        stat_spec = {"statistic": astatic.DP_MEAN,
                     "variable": "EyeHeight",
                     "epsilon": 1,
                     "delta": 0,
                     "ci": astatic.CI_95_ALPHA,
                     "error": "",
                     "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                     "handle_as_fixed": False,
                     "fixed_value": "-10",
                     "locked": False,
                     "label": "EyeHeight"
                     }

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid2 = serializer.save(**dict(opendp_user=self.user_obj))
        # print('stats_valid.success', stats_valid.success)
        self.assertTrue(stats_valid2.success)
        self.assertFalse(stats_valid2.data[0]['valid'])
        print('stats_valid.data', stats_valid2.data)

        user_msg3 = 'The "fixed value" (-10.0) cannot be less than the "min" (-8.0)'

        self.assertEqual(stats_valid2.data[0]['message'], user_msg3)


    def test_90_ok_impute_equals_min(self):
        """(90) Fail: Impute equals min"""
        msgt(self.test_90_ok_impute_equals_min.__doc__)

        analysis_plan = self.analysis_plan

        # invalid min/max
        analysis_plan.variable_info['TypingSpeed']['min'] = -8
        analysis_plan.variable_info['TypingSpeed']['max'] = 5
        analysis_plan.save()

        # Send the dp_statistics for validation
        #
        stat_spec = self.general_stat_spec
        stat_spec["variable"] ="TypingSpeed"
        stat_spec["fixed_value"] = -8

        request_plan = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer = ReleaseValidationSerializer(data=request_plan)
        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.errors == {})

        # Now run the validator
        #
        stats_valid = serializer.save(**dict(opendp_user=self.user_obj))
        # print('stats_valid.success', stats_valid.success)
        self.assertTrue(stats_valid.success)
        self.assertTrue(stats_valid.data[0]['valid'])
        self.assertTrue('accuracy' in stats_valid.data[0])

        # ----------------------------------------------
        # have impute == max
        # ----------------------------------------------
        stat_spec2 = self.general_stat_spec
        stat_spec2["fixed_value"] = 5

        request_plan2 = dict(analysis_plan_id=analysis_plan.object_id,
                            dp_statistics=[stat_spec])

        # Check the basics
        #
        serializer2 = ReleaseValidationSerializer(data=request_plan2)
        self.assertTrue(serializer2.is_valid())

        # Now run the validator
        #
        stats_valid2 = serializer.save(**dict(opendp_user=self.user_obj))
        self.assertTrue(stats_valid2.success)
        self.assertTrue(stats_valid2.data[0]['valid'])
        self.assertTrue('accuracy' in stats_valid2.data[0])

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



"""

           
            {'variable': 'TypingSpeed', 'statistic': 'mean', 'valid': False,
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