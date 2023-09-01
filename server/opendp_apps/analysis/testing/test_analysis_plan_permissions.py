import json
import sys
from http import HTTPStatus
from os.path import abspath, dirname, join

from opendp_apps.analysis.analysis_plan_creator import AnalysisPlanCreator
from opendp_apps.analysis.testing.base_analysis_plan_test import BaseAnalysisPlanTest
from opendp_apps.analysis.validate_release_util import ValidateReleaseUtil
from opendp_apps.model_helpers.msg_util import msgt

CURRENT_DIR = dirname(abspath(__file__))
FIXTURE_DATA_DIR = join(dirname(CURRENT_DIR), 'fixtures')


class AnalysisPlanTest(BaseAnalysisPlanTest):
    fixtures = ['test_analysis_002.json']

    RESTRICTED_ATTRS = ['delta', 'confidence_level', 'dataset_id', 'variable_info', 'dp_statistics']

    def setUp(self):
        super().setUp()

        # Load dp_statistics data for creating plans
        self.dp_stat_info = json.load(open(join(FIXTURE_DATA_DIR, 'stats_data_01.json'), 'r'))

        # Create 4 Plans
        plan_users = [self.user_obj, self.user_obj,
                      self.analyst_user_obj, self.analyst_user_obj]
        plan_no = 0
        remaining_epsilon = 1.0
        for plan_user in plan_users:
            plan_no += 1
            plan_info = self.working_plan_info.copy()
            plan_info['name'] = f'Plan {plan_no}'
            plan_info['description'] = f'Plan {plan_no} description'
            plan_info['analyst_id'] = plan_user.object_id

            plan_epsilon = 0.20
            remaining_epsilon -= plan_epsilon
            plan_info['epsilon'] = plan_epsilon
            # Create a plan
            plan_creator = AnalysisPlanCreator(self.user_obj, plan_info)
            if plan_creator.has_error():
                print('ERRORS', plan_creator.get_error_message())
                return
            self.assertEqual(plan_creator.has_error(), False)

            new_plan = plan_creator.analysis_plan

            # Set the plan's "dp_statistics" field
            new_plan.dp_statistics = [self.dp_stat_info[plan_no - 1]]
            new_plan.save()
            # Set the plan as a class variable, self.plan_1, self.plan_2, etc.
            self.__dict__[f'plan_{plan_no}'] = new_plan

            # check the epsilon
            calc_remaining_epsilon = AnalysisPlanCreator.get_available_epsilon(self.dataset_info)
            self.assertEqual(round(remaining_epsilon, 2), round(calc_remaining_epsilon, 2))

        # Create releases for plans 1 and 2, but not plans 3 and 4
        #
        for plan in [self.plan_1, self.plan_3]:
            release_util = ValidateReleaseUtil.compute_mode(
                plan.analyst,
                plan.object_id)
            if release_util.has_error():
                print('ERRORS', release_util.get_error_message())
                sys.exit(0)
            self.assertFalse(release_util.has_error())

    def test_010_test_plan_permissions(self):
        """
        (10) Test API permissions for AnalysisPlanListViewSet.
        This view set hides AnalysisPlan several fields but includes
         *all* published plans with ReleaseInfo objects
         """
        msgt(self.test_010_test_plan_permissions.__doc__)

        # The user who owns the dataset should see all plans
        #
        self.client.force_login(self.user_obj)
        response = self.client.get(f'{self.API_ANALYSIS_LIST_VIEW_PREFIX}')
        self.assertTrue(response.status_code, HTTPStatus.OK)
        plan_list = response.json()['results']
        self.assertEqual(4, len(plan_list))

        self.check_restricted_attrs_not_there(plan_list)

        # The analyst should see 2 plans + 1 plans from another user with complete releases
        #
        self.client.force_login(self.analyst_user_obj)
        response = self.client.get(f'{self.API_ANALYSIS_LIST_VIEW_PREFIX}')
        self.assertTrue(response.status_code, HTTPStatus.OK)
        plan_list = response.json()['results']
        self.assertEqual(3, len(plan_list))
        expected_object_ids = [str(x.object_id)
                               for x in [self.plan_1, self.plan_3, self.plan_4]]
        for plan in plan_list:
            self.assertTrue(plan['object_id'] in expected_object_ids)

        self.check_restricted_attrs_not_there(plan_list)

        # The non-depositor, non-analyst user should see 2 plans with completed releases
        #
        self.client.force_login(self.another_user)
        response = self.client.get(f'{self.API_ANALYSIS_LIST_VIEW_PREFIX}')
        self.assertTrue(response.status_code, HTTPStatus.OK)
        plan_list = response.json()['results']
        self.assertEqual(2, len(plan_list))
        expected_object_ids = [str(x.object_id) for x in [self.plan_1, self.plan_3]]
        for plan in plan_list:
            self.assertTrue(plan['object_id'] in expected_object_ids)

        self.check_restricted_attrs_not_there(plan_list)

    def test_020_test_plan_permissions(self):
        """
        (20) Test API permissions for AnalysisPlanViewSet--which is more restrictive than AnalysisPlanListViewSet.
         It does not include *all* published plans with ReleaseInfo objects.
         However, it does include variable_info and dp_statistics fields.
        """
        msgt(self.test_020_test_plan_permissions.__doc__)

        # The user who owns the dataset should see all plans
        #
        self.client.force_login(self.user_obj)
        response = self.client.get(f'{self.API_ANALYSIS_PREFIX}')
        self.assertTrue(response.status_code, HTTPStatus.OK)
        plan_list = response.json()['results']
        self.assertEqual(4, len(plan_list))

        self.check_expected_attrs_exist(plan_list)

        # The analyst should see only 2 plans -- their own
        #
        self.client.force_login(self.analyst_user_obj)
        response = self.client.get(f'{self.API_ANALYSIS_PREFIX}')
        self.assertTrue(response.status_code, HTTPStatus.OK)
        plan_list = response.json()['results']
        self.assertEqual(2, len(plan_list))
        expected_object_ids = [str(x.object_id)
                               for x in [self.plan_1, self.plan_3, self.plan_4]]
        for plan in plan_list:
            self.assertTrue(plan['object_id'] in expected_object_ids)

        self.check_expected_attrs_exist(plan_list)

        # The non-depositor, non-analyst user should see 2 plans with completed releases
        #
        self.client.force_login(self.another_user)
        response = self.client.get(f'{self.API_ANALYSIS_PREFIX}')
        self.assertTrue(response.status_code, HTTPStatus.OK)
        plan_list = response.json()['results']
        self.assertEqual(0, len(plan_list))

    def check_restricted_attrs_not_there(self, plan_list):
        """Make sure restricted attributes are not in the plan_list"""
        for info in plan_list:
            for attr in self.RESTRICTED_ATTRS:
                self.assertTrue(attr not in info)

    def check_expected_attrs_exist(self, plan_list):
        """Make sure restricted attributes are not in the plan_list"""
        for info in plan_list:
            for attr in self.RESTRICTED_ATTRS:
                self.assertTrue(attr in info)
