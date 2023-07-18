import json
import uuid
from datetime import timedelta, datetime
from http import HTTPStatus
from os.path import abspath, dirname, join

from django.contrib.auth import get_user_model
from django.core.files import File as DjangoFileObject
from django.test import TestCase
from rest_framework.test import APIClient

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.analysis_plan_creator import AnalysisPlanCreator
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.dataset import static_vals as dstatic
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.msg_util import msgt

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class AnalysisPlanTest(TestCase):
    fixtures = ['test_analysis_002.json']

    def setUp(self):
        """Create user object and define file to upload"""

        self.API_PREFIX = '/api/analysis-plan/'

        # Create a OpenDP User object
        #
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dp_depositor')
        self.analyst_user_obj, _created = get_user_model().objects.get_or_create(username='dp_analyst')
        self.another_user, _created = get_user_model().objects.get_or_create(username='another_user')

        self.client = APIClient()
        self.client.force_login(self.user_obj)

        expiration_date = datetime.now() + timedelta(days=5)
        self.expiration_date_str = datetime.strftime(expiration_date, '%Y-%m-%d')

        # Define a file to upload
        self.test_file_name = join('teacher_survey', 'teacher_survey.csv')
        self.upload_name = 'Teacher Survey'
        test_file = join(TEST_DATA_DIR, self.test_file_name)

        # Attach the file to the DataSetInfo object and
        #   make sure to start with epsilon = 1.0
        self.dataset_info = DataSetInfo.objects.get(id=2)
        self.dataset_info.source_file.save(self.upload_name, DjangoFileObject(open(test_file, 'rb')))
        self.dataset_info.depositor_setup_info.epsilon = 1.0
        self.dataset_info.save()

        self.dataset_object_id = str(self.dataset_info.object_id)

        self.working_plan_info = dict(object_id=self.dataset_object_id,
                                      name='Teacher survey plan',
                                      description='Release DP Statistics for the teacher survey, version 1',
                                      epsilon=0.25,
                                      expiration_date=self.expiration_date_str)
        # print(json.dumps(self.working_plan_info, indent=4))

    def test_10_create_plan(self):
        """(10) Create AnalysisPlan using AnalysisPlanUtil"""
        msgt(self.test_10_create_plan.__doc__)

        # --------------------------------------------------
        # Create plan 1 with .25 epsilon
        # --------------------------------------------------
        plan_info = self.working_plan_info.copy()

        plan_util = AnalysisPlanCreator(self.user_obj, plan_info)

        self.assertEqual(plan_util.has_error(), False)
        if plan_util.has_error():
            print('ERRORS', plan_util.get_error_message())
            return

        self.assertEqual(plan_util.analysis_plan.name, plan_info['name'])
        self.assertEqual(plan_util.analysis_plan.description, plan_info['description'])
        self.assertEqual(plan_util.analysis_plan.epsilon, plan_info['epsilon'])
        self.assertEqual(plan_util.analysis_plan.expiration_date.strftime('%Y-%m-%d'),
                         plan_info['expiration_date'])

        remaining_epsilon = AnalysisPlanCreator.get_available_epsilon(self.dataset_info)
        self.assertEqual(remaining_epsilon, 0.75)

        # --------------------------------------------------
        # Create plan 2 with .50 epsilon
        # --------------------------------------------------
        plan_info['name'] = 'Teacher survey plan 2'
        plan_info['description'] = 'Release DP Statistics for the teacher survey, version 2'
        plan_info['epsilon'] = 0.50

        plan_util = AnalysisPlanCreator(self.user_obj,
                                        plan_info)

        if plan_util.has_error():
            print('ERRORS', plan_util.get_error_message())
            return

        self.assertEqual(plan_util.has_error(), False)
        self.assertEqual(plan_util.analysis_plan.name, plan_info['name'])
        self.assertEqual(plan_util.analysis_plan.description, plan_info['description'])
        self.assertEqual(plan_util.analysis_plan.epsilon, plan_info['epsilon'])
        self.assertEqual(plan_util.analysis_plan.expiration_date.strftime('%Y-%m-%d'),
                         plan_info['expiration_date'])

        remaining_epsilon = AnalysisPlanCreator.get_available_epsilon(self.dataset_info)
        self.assertEqual(remaining_epsilon, 0.25)

        # --------------------------------------------------
        # Create plan 3 with .50 epsilon -- should exceed epsilon
        # --------------------------------------------------
        plan_info['name'] = 'Teacher survey plan 3'
        plan_info['description'] = 'Release DP Statistics for the teacher survey, version 3'
        plan_info['epsilon'] = 0.50

        plan_util = AnalysisPlanCreator(self.user_obj, plan_info)

        self.assertEqual(plan_util.has_error(), True)

        expected_msg = astatic.ERR_MSG_NOT_ENOUGH_EPSILON_AVAILABLE.format(available_epsilon=0.25,
                                                                           requested_epsilon=0.50)
        self.assertEqual(plan_util.get_error_message(), expected_msg)

    def test_15_create_plan_via_api(self):
        """(15) Create AnalysisPlan using the API"""
        msgt(self.test_15_create_plan_via_api.__doc__)

        payload = self.working_plan_info.copy()

        response = self.client.post(self.API_PREFIX,
                                    json.dumps(payload),
                                    content_type='application/json')

        # print('response.json', json.dumps(response.json(), indent=2))

        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertEqual(response.json()['name'], payload['name'])
        self.assertEqual(response.json()['description'], payload['description'])
        self.assertEqual(response.json()['epsilon'], payload['epsilon'])
        self.assertEqual(response.json()['user_step'], AnalysisPlan.AnalystSteps.STEP_0000_INITIALIZED)
        self.assertEqual(response.json()['dp_statistics'], None)
        self.assertEqual(response.json()['is_complete'], False)
        self.assertEqual(response.json()['release_info'], None)
        self.assertEqual(response.json()['expiration_date'][:10],
                         payload['expiration_date'])
        self.assertTrue('variable_info' in response.json())
        self.assertTrue('age' in response.json()['variable_info'])

        new_plan_object_id = response.json()['object_id']

        # -----------------------------------------
        # Retrieve the new Analysis Plan via API
        # -----------------------------------------
        response = self.client.get(f'{self.API_PREFIX}{new_plan_object_id}/',
                                   content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        the_plan2 = response.json()
        # print('the_plan2', json.dumps(the_plan2, indent=2))

        self.assertEqual(the_plan2['object_id'], new_plan_object_id)
        self.assertEqual(the_plan2['name'], payload['name'])
        self.assertEqual(the_plan2['description'], payload['description'])
        self.assertEqual(the_plan2['epsilon'], payload['epsilon'])

        self.assertFalse(the_plan2['is_complete'])
        self.assertEqual(the_plan2['user_step'],
                         AnalysisPlan.AnalystSteps.STEP_0000_INITIALIZED)
        self.assertEqual(the_plan2['variable_info'],
                         self.dataset_info.depositor_setup_info.variable_info)
        self.assertEqual(the_plan2['dp_statistics'], None)

    def test_20_fail_no_dataset_id(self):
        """(20) Fail b/c no dataset id"""
        msgt(self.test_20_fail_no_dataset_id.__doc__)

        plan_util = AnalysisPlanCreator(self.user_obj, {})

        self.assertTrue(plan_util.has_error())
        self.assertEqual(plan_util.get_error_message(), astatic.ERR_MSG_DATASET_ID_REQUIRED)

    def test_30_fail_no_user(self):
        """(30) Fail b/c no user"""
        msgt(self.test_30_fail_no_user.__doc__)

        plan_util = AnalysisPlanCreator(None, {'object_id': self.dataset_object_id})

        self.assertTrue(plan_util.has_error())
        self.assertEqual(plan_util.get_error_message(), astatic.ERR_MSG_USER_REQUIRED)

    def test_40_fail_bad_dataset_id(self):
        """(40) Fail b/c bad dataset id"""
        msgt(self.test_40_fail_bad_dataset_id.__doc__)

        nonsense_dataset_id = str(uuid.uuid4())
        plan_util = AnalysisPlanCreator(self.user_obj, {'object_id': nonsense_dataset_id})

        self.assertTrue(plan_util.has_error())
        self.assertEqual(plan_util.get_error_message(), astatic.ERR_MSG_NO_DATASET)

    def test_50_depositor_setup_incomplete(self):
        """(50) Fail b/c DepositorSetupInfo is incomplete"""
        msgt(self.test_50_depositor_setup_incomplete.__doc__)

        dataset_info = DataSetInfo.objects.get(id=2)
        dataset_info.depositor_setup_info.variable_info = None
        dataset_info.depositor_setup_info.save()

        self.assertEqual(dataset_info.depositor_setup_info.variable_info, None)

        plan_util = AnalysisPlanCreator(self.user_obj,
                                        {'object_id': self.dataset_object_id})

        # Plan should fail with error message
        self.assertTrue(plan_util.has_error())
        self.assertEqual(plan_util.get_error_message(), astatic.ERR_MSG_SETUP_INCOMPLETE)

    def test_60_bad_dataset_id_via_api(self):
        """(60) Fail using bad dataset id (not a UUID) via the API"""
        msgt(self.test_60_bad_dataset_id_via_api.__doc__)

        payload = json.dumps({"object_id": 'mickey mouse'})  # str(dataset_info.object_id)})
        response = self.client.post(self.API_PREFIX,
                                    payload,
                                    content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json()['success'], False)
        self.assertTrue(response.json()['message'].find('Must be a valid UUID') > -1)

    def test_70_invalid_dataset_id_via_api(self):
        """(70) Fail using invalid dataset ID (but it is a valid UUID)"""
        msgt(self.test_70_invalid_dataset_id_via_api.__doc__)

        dataset_info = DataSetInfo.objects.get(id=2)

        nonsense_dataset_id = str(uuid.uuid4())

        payload = json.dumps({"object_id": str(nonsense_dataset_id)})
        response = self.client.post(self.API_PREFIX,
                                    payload,
                                    content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        jresp = response.json()
        self.assertEqual(jresp['success'], False)
        self.assertTrue(jresp['message'].find(dstatic.ERR_MSG_DATASET_INFO_NOT_FOUND) > -1)

    def test_80_update_plan(self):
        """(80) Update AnalysisPlan"""
        msgt(self.test_80_update_plan.__doc__)

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

    def test_82_update_plan_wrong_analyst(self):
        """(82) Update plan where user isn't the assigned analyst"""
        msgt(self.test_82_update_plan_wrong_analyst.__doc__)

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

    def test_84_create_plan_bad_analyst_id(self):
        """(84) Update plan where user isn't the assigned analyst"""
        msgt(self.test_84_create_plan_bad_analyst_id.__doc__)

        payload = self.working_plan_info
        payload['analyst_id'] = str(uuid.uuid4())

        plan_creator = AnalysisPlanCreator(self.user_obj, payload)

        # -------------------------------------------------------------------
        # (a) plan creation should fail
        # -------------------------------------------------------------------
        self.assertTrue(plan_creator.has_error() is True)
        self.assertEqual(plan_creator.get_err_msg(), astatic.ERR_MSG_PLAN_INFO_ANALYST_ID_INVALID)

        # -------------------------------------------------------------------
        # (b) do it again via API, should also fail
        # -------------------------------------------------------------------
        response = self.client.post(self.API_PREFIX,
                                    json.dumps(payload),
                                    content_type='application/json')

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json()['message'], astatic.ERR_MSG_PLAN_INFO_ANALYST_ID_INVALID)

    def test_90_update_plan_fail_bad_id(self):
        """(90) Update AnalysisPlan, fail w/ bad id"""
        msgt(self.test_90_update_plan_fail_bad_id.__doc__)

        nonsense_dataset_id = str(uuid.uuid4())

        payload = json.dumps(dict(dp_statistics=dict(hi='there')))

        response = self.client.patch(f'{self.API_PREFIX}{nonsense_dataset_id}/',
                                     payload,
                                     content_type='application/json')

        self.assertEqual(response.status_code, 404)

    def test_100_update_plan_bad_fields(self):
        """(100) Update AnalysisPlan, fail w/ bad fields"""
        msgt(self.test_100_update_plan_bad_fields.__doc__)

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
            problem_field_str='epsilon, user_step, zebra')
        self.assertEqual(response.json()['message'], user_msg)

    def test_110_test_delete_no_release(self):
        """(110) Delete AnalysisPlan w/ no ReleaseInfo"""
        msgt(self.test_110_test_delete_no_release.__doc__)

        # Create the AnalysisPlan
        #
        plan_util = AnalysisPlanCreator(self.user_obj, self.working_plan_info)
        self.assertTrue(plan_util.has_error() is False)

        # Delete the plan!
        #
        plan_object_id = plan_util.analysis_plan.object_id

        response = self.client.delete(f'{self.API_PREFIX}{plan_object_id}/')

        # Works fine, HTTP 204
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_120_test_delete_dataset_owner(self):
        """(120) Delete AnalysisPlan by the dataset owner"""
        msgt(self.test_120_test_delete_dataset_owner.__doc__)

        # Create the AnalysisPlan
        #
        self.working_plan_info['analyst_id'] = str(self.analyst_user_obj.object_id)
        plan_util = AnalysisPlanCreator(self.user_obj, self.working_plan_info)
        self.assertTrue(plan_util.has_error() is False)

        # Delete the plan!
        #
        plan_object_id = plan_util.analysis_plan.object_id

        response = self.client.delete(f'{self.API_PREFIX}{plan_object_id}/')

        # AnalysisPlan not found, HTTP 204
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_130_test_delete_user_no_perms(self):
        """(130) Delete AnalysisPlan by user w/o permission"""
        msgt(self.test_130_test_delete_user_no_perms.__doc__)

        # Create the AnalysisPlan
        #
        self.working_plan_info['analyst_id'] = str(self.analyst_user_obj.object_id)
        plan_util = AnalysisPlanCreator(self.user_obj, self.working_plan_info)
        self.assertTrue(plan_util.has_error() is False)

        # Delete the plan!
        #   Logged in user is the self.opendp_user_obj, not self.analyst_user_obj so AnalysisPlan not found
        #
        plan_object_id = plan_util.analysis_plan.object_id

        self.client.force_login(self.another_user)

        response = self.client.delete(f'{self.API_PREFIX}{plan_object_id}/')

        # AnalysisPlan not found, HTTP 404
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_140_list_plans(self):
        """(140) List AnalysisPlans using different users w/ varying permissions"""
        msgt(self.test_140_list_plans.__doc__)

        # Create two AnalysisPlans
        #
        plan1 = self.working_plan_info.copy()
        plan_util = AnalysisPlanCreator(self.user_obj, plan1)
        self.assertTrue(plan_util.has_error() is False)
        analysis_plan1 = plan_util.analysis_plan

        plan2 = self.working_plan_info.copy()
        plan2['analyst_id'] = str(self.analyst_user_obj.object_id)
        plan2['name'] = 'Plan 2'
        plan_util2 = AnalysisPlanCreator(self.user_obj, plan2)
        self.assertTrue(plan_util2.has_error() is False)
        analysis_plan2 = plan_util2.analysis_plan

        # List the plans w/ call by the dataset owner
        #
        response = self.client.get(f'{self.API_PREFIX}')
        self.assertTrue(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['count'], 2)
        self.assertEqual(response.json()['results'][0]['object_id'], str(analysis_plan1.object_id))

        # List the plans w/ call by the analyst
        #
        self.client.force_login(self.analyst_user_obj)
        response = self.client.get(f'{self.API_PREFIX}')
        self.assertTrue(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['count'], 1)
        self.assertEqual(response.json()['results'][0]['object_id'], str(analysis_plan2.object_id))
        self.assertEqual(response.json()['results'][0]['name'], 'Plan 2')

        print(json.dumps(response.json(), indent=4))
        # List the plans w/ call by user with no permission
        #
        self.client.force_login(self.another_user)
        response = self.client.get(f'{self.API_PREFIX}')
        self.assertTrue(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json()['count'], 0)
