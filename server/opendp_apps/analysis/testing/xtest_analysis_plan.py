import json
import uuid
from os.path import abspath, dirname, join
from unittest import skip

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.dataset import static_vals as dstatic
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.msg_util import msgt

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(CURRENT_DIR), 'test_files')


class AnalysisPlanTest(TestCase):
    fixtures = ['test_analysis_001.json', ]

    def setUp(self):
        # test client
        self.client = APIClient()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        self.client.force_login(self.user_obj)

    def test_10_create_plan(self):
        """(10) Create AnalysisPlan directly"""
        msgt(self.test_10_create_plan.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)

        plan_util = AnalysisPlanUtil.create_plan(dataset_info.object_id,
                                                 self.user_obj)

        # did plan creation work?
        self.assertTrue(plan_util.success)

        # look at the plan data/defaults
        the_plan = plan_util.data

        # should have same user and dataset
        self.assertEqual(the_plan.analyst.object_id, self.user_obj.object_id)

        # check default settings
        self.assertEqual(the_plan.dataset.object_id, dataset_info.object_id)
        self.assertFalse(the_plan.is_complete)
        self.assertEqual(the_plan.user_step,
                         AnalysisPlan.AnalystSteps.STEP_0700_VARIABLES_CONFIRMED)

        self.assertEqual(the_plan.variable_info,
                         dataset_info.depositor_setup_info.variable_info)
        self.assertEqual(the_plan.dp_statistics, None)

    def test_15_create_plan_via_api(self):
        """(15) Create AnalysisPlan using the API"""
        msgt(self.test_15_create_plan_via_api.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)

        payload = json.dumps({"object_id": str(dataset_info.object_id)})
        response = self.client.post('/api/analyze/',
                                    payload,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 201)
        the_plan = response.json()

        # should have same user and dataset
        plan_object_id = the_plan['object_id']
        plan_name = the_plan['name']
        self.assertEqual(the_plan['analyst'], str(self.user_obj.object_id))
        self.assertEqual(the_plan['dataset'], str(dataset_info.object_id))

        # check default settings
        self.assertFalse(the_plan['is_complete'])
        self.assertEqual(the_plan['user_step'],
                         AnalysisPlan.AnalystSteps.STEP_0700_VARIABLES_CONFIRMED)
        self.assertEqual(the_plan['variable_info'],
                         dataset_info.depositor_setup_info.variable_info)
        self.assertEqual(the_plan['dp_statistics'], None)

        # -----------------------------------------
        # Retrieve the new Analysis Plan via API
        # -----------------------------------------
        response = self.client.get(f'/api/analyze/{plan_object_id}/',
                                   content_type='application/json')

        self.assertEqual(response.status_code, 200)
        the_plan2 = response.json()
        # self.assertEqual(jresp.get('success'), True)
        self.assertEqual(the_plan2['object_id'], plan_object_id)
        self.assertEqual(the_plan2['name'], plan_name)

        self.assertFalse(the_plan2['is_complete'])
        self.assertEqual(the_plan2['user_step'],
                         AnalysisPlan.AnalystSteps.STEP_0700_VARIABLES_CONFIRMED)
        self.assertEqual(the_plan2['variable_info'],
                         dataset_info.depositor_setup_info.variable_info)
        self.assertEqual(the_plan2['dp_statistics'], None)

    def test_20_fail_no_dataset_id(self):
        """(20) Fail b/c no dataset id"""
        msgt(self.test_20_fail_no_dataset_id.__doc__)

        plan_util = AnalysisPlanUtil.create_plan(None,
                                                 self.user_obj)
        self.assertFalse(plan_util.success)
        self.assertEqual(plan_util.message, astatic.ERR_MSG_DATASET_ID_REQUIRED)

    def test_30_fail_no_user(self):
        """(30) Fail b/c no user"""
        msgt(self.test_30_fail_no_user.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)
        plan_util = AnalysisPlanUtil.create_plan(dataset_info.object_id,
                                                 None)
        self.assertFalse(plan_util.success)
        self.assertEqual(plan_util.message, astatic.ERR_MSG_USER_REQUIRED)

    def test_40_fail_bad_dataset_id(self):
        """(40) Fail b/c bad dataset id"""
        msgt(self.test_40_fail_bad_dataset_id.__doc__)

        nonsense_dataset_id = uuid.uuid4()
        plan_util = AnalysisPlanUtil.create_plan(nonsense_dataset_id,
                                                 self.user_obj)
        self.assertFalse(plan_util.success)
        self.assertEqual(plan_util.message, astatic.ERR_MSG_NO_DATASET)

    def test_50_depositor_setup_incomplete(self):
        """(50) Fail b/c DepositorSetupInfo is incomplete"""
        msgt(self.test_50_depositor_setup_incomplete.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)
        dataset_info.depositor_setup_info.variable_info = None
        dataset_info.depositor_setup_info.save()

        self.assertEqual(dataset_info.depositor_setup_info.variable_info, None)

        plan_util = AnalysisPlanUtil.create_plan(dataset_info.object_id,
                                                 self.user_obj)

        # Plan should fail with error message
        self.assertFalse(plan_util.success)
        self.assertEqual(plan_util.message, astatic.ERR_MSG_SETUP_INCOMPLETE)

    def test_60_bad_dataset_id_via_api(self):
        """(60) Fail using bad dataset id (not a UUID) via the API"""
        msgt(self.test_60_bad_dataset_id_via_api.__doc__)

        payload = json.dumps({"object_id": 'mickey mouse'})  # str(dataset_info.object_id)})
        response = self.client.post('/api/analyze/',
                                    payload,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 400)
        jresp = response.json()
        self.assertEqual(jresp['success'], False)
        self.assertTrue(jresp['message'].find('Must be a valid UUID') > -1)

    def test_70_invalid_dataset_id_via_api(self):
        """(70) Fail using invalid dataset ID (but it is a valid UUID)"""
        msgt(self.test_70_invalid_dataset_id_via_api.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)

        nonsense_dataset_id = uuid.uuid4()

        payload = json.dumps({"object_id": str(nonsense_dataset_id)})
        response = self.client.post('/api/analyze/',
                                    payload,
                                    content_type='application/json')

        self.assertEqual(response.status_code, 400)
        jresp = response.json()
        self.assertEqual(jresp['success'], False)
        self.assertTrue(jresp['message'].find( \
            dstatic.ERR_MSG_DATASET_INFO_NOT_FOUND) > -1)

    def test_80_update_plan(self):
        """(80) Update AnalysisPlan"""
        msgt(self.test_80_update_plan.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)

        plan_util = AnalysisPlanUtil.create_plan(dataset_info.object_id,
                                                 self.user_obj)

        # did plan creation work?
        self.assertTrue(plan_util.success)

        #
        # Update the plan!
        #
        plan_object_id = plan_util.data.object_id
        payload = json.dumps(dict(dp_statistics=dict(hi='there')))
        response = self.client.patch(f'/api/analyze/{plan_object_id}/',
                                     payload,
                                     content_type='application/json')

        self.assertEqual(response.status_code, 200)
        jresp = response.json()

        self.assertEqual(jresp['dp_statistics'], dict(hi='there'))

    def test_90_update_plan_fail_bad_id(self):
        """(90) Update AnalysisPlan, fail w/ bad id"""
        msgt(self.test_90_update_plan_fail_bad_id.__doc__)

        nonsense_dataset_id = uuid.uuid4()

        payload = json.dumps(dict(dp_statistics=dict(hi='there')))
        response = self.client.patch(f'/api/analyze/{nonsense_dataset_id}/',
                                     payload,
                                     content_type='application/json')

        self.assertEqual(response.status_code, 404)

    def test_100_update_plan_bad_fields(self):
        """(100) Update AnalysisPlan, fail w/ bad fields"""
        msgt(self.test_100_update_plan_bad_fields.__doc__)

        dataset_info = DataSetInfo.objects.get(id=4)

        plan_util = AnalysisPlanUtil.create_plan(dataset_info.object_id,
                                                 self.user_obj)

        # did plan creation work?
        self.assertTrue(plan_util.success)

        #
        # Update the plan!
        #
        plan_object_id = plan_util.data.object_id

        payload = json.dumps(dict(name='haha'))
        response = self.client.patch(f'/api/analyze/{plan_object_id}/',
                                     payload,
                                     content_type='application/json')

        self.assertEqual(response.status_code, 400)

        jresp = response.json()
        self.assertTrue(jresp['message'].find(astatic.ERR_MSG_FIELDS_NOT_UPDATEABLE) > -1)
