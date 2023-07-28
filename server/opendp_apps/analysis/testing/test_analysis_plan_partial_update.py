import json
import uuid
from http import HTTPStatus
from os.path import abspath, dirname, join

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.analysis_plan_creator import AnalysisPlanCreator
from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis.testing.base_analysis_plan_test import BaseAnalysisPlanTest
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils import datetime_util

class AnalysisPlanTest(BaseAnalysisPlanTest):
    fixtures = ['test_analysis_002.json']

    def setUp(self):
        super().setUp()

    def test_100_update_plan(self):
        """(100) Update AnalysisPlan"""
        msgt(self.test_100_update_plan.__doc__)

        # (a) Create a plan
        #
        payload = self.working_plan_info
        payload['analyst_id'] = str(self.analyst_user_obj.object_id)

        plan_creator = AnalysisPlanCreator(self.user_obj, payload)

        # did plan creation work?
        self.assertTrue(plan_creator.has_error() is False)

        # (b) Have the Analyst update the plan!
        #
        plan_object_id = plan_creator.analysis_plan.object_id

        self.client.force_login(self.analyst_user_obj)

        # note: not checking **validity** of dp_statistics or variable_info here
        update_data = {'dp_statistics': {'hi': 'there'},
                       'variable_info': {'age': {'type': 'Integer'}},
                       'name': 'Teacher survey plan, version 2a',
                       'description': 'A new description',
                       'wizard_step': 'yellow brick road'}

        response = self.client.patch(f'{self.API_PREFIX}{plan_object_id}/',
                                     json.dumps(update_data),
                                     content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        jresp = response.json()

        # print(json.dumps(jresp, indent=2))

        self.assertEqual(jresp['dp_statistics'], update_data['dp_statistics'])
        self.assertEqual(jresp['variable_info'], update_data['variable_info'])
        self.assertEqual(jresp['name'], update_data['name'])
        self.assertEqual(jresp['description'], update_data['description'])
        self.assertEqual(jresp['wizard_step'], update_data['wizard_step'])

    def test_110_update_plan_wrong_analyst(self):
        """(110) Update plan with an invalid user/analyst"""
        msgt(self.test_110_update_plan_wrong_analyst.__doc__)

        # (a) Create a plan
        #
        payload = self.working_plan_info
        payload['analyst_id'] = str(self.analyst_user_obj.object_id)

        plan_creator = AnalysisPlanCreator(self.user_obj, payload)

        # did plan creation work?
        self.assertTrue(plan_creator.has_error() is False)

        # -------------------------------------------------------------------
        # (b) Have the Depositor, not the assigned analyst update the plan!
        #   - should fail!
        # -------------------------------------------------------------------
        plan_object_id = plan_creator.analysis_plan.object_id

        self.client.force_login(self.user_obj)

        # note: not checking **validity** of dp_statistics or variable_info here
        update_data = {'dp_statistics': {'hi': 'there'},
                       'variable_info': {'age': {'type': 'Integer'}},
                       'name': 'Teacher survey plan, version 2a',
                       'description': 'A new description',
                       'wizard_step': 'yellow brick road'}

        response = self.client.patch(f'{self.API_PREFIX}{plan_object_id}/',
                                     json.dumps(update_data),
                                     content_type='application/json')

        # Should not be found!
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        # -------------------------------------------------------------------
        # (c) Have another user, not the assigned analyst update the plan!
        #    - should fail
        # -------------------------------------------------------------------
        self.client.force_login(self.another_user)

        response = self.client.patch(f'{self.API_PREFIX}{plan_object_id}/',
                                     json.dumps(update_data),
                                     content_type='application/json')

        # Again, should not be found!
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        # -------------------------------------------------------------------
        # (d) Finally, have the assigned analyst update the plan!
        # -------------------------------------------------------------------
        self.client.force_login(self.analyst_user_obj)

        response = self.client.patch(f'{self.API_PREFIX}{plan_object_id}/',
                                     json.dumps(update_data),
                                     content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        jresp = response.json()
        self.assertEqual(jresp['dp_statistics'], update_data['dp_statistics'])
        self.assertEqual(jresp['variable_info'], update_data['variable_info'])
        self.assertEqual(jresp['name'], update_data['name'])
        self.assertEqual(jresp['description'], update_data['description'])
        self.assertEqual(jresp['wizard_step'], update_data['wizard_step'])

    def test_120_update_plan_fail_bad_id(self):
        """(120) Update AnalysisPlan, fail w/ bad id"""
        msgt(self.test_120_update_plan_fail_bad_id.__doc__)

        nonsense_dataset_id = str(uuid.uuid4())

        payload = json.dumps(dict(dp_statistics=dict(hi='there')))

        response = self.client.patch(f'{self.API_PREFIX}{nonsense_dataset_id}/',
                                     payload,
                                     content_type='application/json')

        self.assertEqual(response.status_code, 404)

    def test_130_update_expired_analysis_plan(self):
        """(130) Update an expired AnalysisPlan -- should fail"""
        msgt(self.test_130_update_expired_analysis_plan.__doc__)

        # Create the AnalysisPlan
        #
        plan_util = AnalysisPlanCreator(self.user_obj, self.working_plan_info)
        self.assertTrue(plan_util.has_error() is False)

        # Make the expiration date yesterday
        #
        analysis_plan = plan_util.analysis_plan
        analysis_plan.expiration_date = datetime_util.get_expiration_date(days=0, microseconds=-1)
        analysis_plan.save()

        # Try to make an update w/ valid data but a bad expiration date
        #
        self.client.force_login(self.user_obj)

        # note: not checking **validity** of dp_statistics or variable_info here
        update_data = {'description': 'A new description',
                       'wizard_step': 'yellow brick road'}

        response = self.client.patch(f'{self.API_PREFIX}{analysis_plan.object_id}/',
                                     json.dumps(update_data),
                                     content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json()['message'], astatic.ERR_MSG_ANALYSIS_PLAN_EXPIRED)

    def test_140_update_plan_bad_fields(self):
        """(140) Update AnalysisPlan, fail w/ bad fields"""
        msgt(self.test_140_update_plan_bad_fields.__doc__)

        payload = self.working_plan_info

        plan_util = AnalysisPlanCreator(self.user_obj, payload)

        # did plan creation work?
        self.assertTrue(plan_util.has_error() is False)

        #
        # Update the plan!
        #
        plan_object_id = plan_util.analysis_plan.object_id

        payload = dict(epsilon=2.0,
                       user_step=AnalysisPlan.AnalystSteps.STEP_0700_VARIABLES_CONFIRMED,
                       zebra='stripes')

        response = self.client.patch(f'{self.API_PREFIX}{plan_object_id}/',
                                     json.dumps(payload),
                                     content_type='application/json')

        self.assertEqual(response.status_code, 400)
        user_msg = astatic.ERR_MSG_FIELDS_NOT_UPDATEABLE.format(
            problem_field_str='user_step, zebra')
        self.assertEqual(response.json()['message'], user_msg)

    def test_150_update_plan_with_release(self):
        """(150) Update AnalysisPlan that has a release. Only the "wizard_step" should be updated"""
        msgt(self.test_150_update_plan_with_release.__doc__)

        plan_info = self.working_plan_info.copy()

        plan_util = AnalysisPlanCreator(self.user_obj, plan_info)

        self.assertEqual(plan_util.has_error(), False)

        analysis_plan = plan_util.analysis_plan
        plan_object_id = analysis_plan.object_id

        placeholder_release = ReleaseInfo(dataset=analysis_plan.dataset,
                                          epsilon_used=analysis_plan.dataset.depositor_setup_info.epsilon,
                                          dp_release={'zirp': 'but why?'})
        placeholder_release.save()
        analysis_plan.release_info = placeholder_release
        analysis_plan.is_complete = True
        analysis_plan.dp_statistics = {'foo': 'bar'}
        analysis_plan.user_step = AnalysisPlan.AnalystSteps.STEP_1200_PROCESS_COMPLETE  # not true, but for testing
        analysis_plan.save()

        print('analysis_plan', analysis_plan.object_id)

        # Note: Reject b/c dp_statistics, variable_info, and is_complete are not updatable
        #
        update_data = {'dp_statistics': {'place': 'sardinia', 'temp (F)': 104},
                       'variable_info': {'age': {'meta': 'some data'}},
                       'name': 'Teacher survey extraordinaire',
                       'is_complete': False,
                       'wizard_step': 'Barbenheimer'}

        response = self.client.patch(f'{self.API_PREFIX}{plan_object_id}/',
                                     json.dumps(update_data),
                                     content_type='application/json')

        # print(json.dumps(response.json(), indent=4))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json()['message'],
                         'These fields are not updatable: dp_statistics, variable_info, is_complete')

    def test_160_update_plan_no_data(self):
        """(160) Update AnalysisPlan w/o any update data"""
        msgt(self.test_160_update_plan_no_data.__doc__)

        plan_info = self.working_plan_info.copy()

        plan_util = AnalysisPlanCreator(self.user_obj, plan_info)

        self.assertEqual(plan_util.has_error(), False)

        update_data = {}

        response = self.client.patch(f'{self.API_PREFIX}{plan_util.analysis_plan.object_id}/',
                                     json.dumps(update_data),
                                     content_type='application/json')

        print(json.dumps(response.json(), indent=4))
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        # Should only update the wizard_step
        self.assertEqual(response.json()['message'], astatic.ERR_MSG_NO_FIELDS_TO_UPDATE)
