import json
from http import HTTPStatus
from os.path import abspath, dirname, join

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataset import static_vals as dstatic
from opendp_apps.dataset.models import DepositorSetupInfo
from opendp_apps.dataset.tests.dataset_test_base import DatasetTestBase
from opendp_apps.model_helpers.msg_util import msgt

CURRENT_DIR = dirname(abspath(__file__))
FIXTURE_DATA_DIR = join(dirname(CURRENT_DIR), 'fixtures')
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class TestUpdateDepositorInfo(DatasetTestBase):
    maxDiff = None

    def setUp(self):
        super().setUp()

    def test_100_update_depositor_info(self):
        """(100) Update depositor info including epsilon questions, dataset questions,
            variable_info, epsilon, delta, etc."""
        msgt(self.test_100_update_depositor_info.__doc__)

        # (1) Upload a file
        #
        jresp = self.upload_file_via_api()

        # (2) Get the dataset info
        #
        ds_object_id = jresp['object_id']
        ds_info = self.get_dataset_info_via_api(ds_object_id)
        # print('ds_info', ds_info)

        # (3) Update depositor info: epsilon questions, dataset_questions
        #
        setup_object_id = ds_info['depositor_setup_info']['object_id']

        partial_update_url = f'{self.API_DEPOSIT}{setup_object_id}/'

        new_epsilon_questions = {"secret_sample": "no",
                                 "population_size": "7000",
                                 "observations_number_can_be_public": 'yes'}

        new_dataset_questions = {"radio_best_describes": "notHarmButConfidential",
                                 "radio_only_one_individual_per_row": "yes",
                                 "radio_depend_on_private_information": "yes"}

        # TODO: note: "user_step" is ignored, but kept for now for MVP work
        update_payload = dict(epsilon_questions=new_epsilon_questions,
                              dataset_questions=new_dataset_questions,
                              user_step=DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        # print(update_resp.json())
        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['epsilon_questions'], new_epsilon_questions)
        self.assertEqual(update_resp_json['dataset_questions'], new_dataset_questions)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0200_VALIDATED))

        # (4) Update depositor info: variable_info
        #
        new_variable_info = json.load(open(join(FIXTURE_DATA_DIR, 'test_data_profile_teacher_survey.json'), 'r'))

        update_payload = dict(variable_info=new_variable_info)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['variable_info'], new_variable_info)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE))

        # print('update_resp_json', update_resp_json)

        # (5) Update depositor info: default_epsilon, epsilon
        #
        new_default_epsilon = 0.5
        new_default_delta = astatic.DELTA_10_NEG_7
        new_epsilon = 0.75

        update_payload = dict(default_epsilon=new_default_epsilon,
                              epsilon=new_epsilon,
                              default_delta=new_default_delta)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        # print('update_resp.update_resp', update_resp.status_code)
        # print('update_resp.content', update_resp.content)
        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()

        self.assertEqual(update_resp_json['is_complete'], False)
        # Should not be able to update the default epsilon or default delta!
        #
        self.assertNotEqual(update_resp_json['default_epsilon'], new_default_epsilon)
        self.assertNotEqual(update_resp_json['default_delta'], new_default_delta)

        self.assertEqual(update_resp_json['epsilon'], new_epsilon)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0600_EPSILON_SET))

        print(json.dumps(update_resp_json, indent=4))

    def test_110_update_depositor_info(self):
        """(110) Test that epsilon/dataset questions can have empty string values
        and that epsilon/delta may be null. Note, the API calls are okay but do not advance
        the user_step."""
        msgt(self.test_110_update_depositor_info.__doc__)

        # (1) Upload a file
        #
        jresp = self.upload_file_via_api()

        # (2) Get the dataset info
        #
        ds_object_id = jresp['object_id']
        ds_info = self.get_dataset_info_via_api(ds_object_id)
        # print('ds_info', ds_info)

        # (3) Update depositor info: epsilon questions, dataset_questions
        #
        setup_object_id = ds_info['depositor_setup_info']['object_id']

        partial_update_url = f'{self.API_DEPOSIT}{setup_object_id}/'

        new_dataset_questions = {"radio_best_describes": "",
                                 "radio_only_one_individual_per_row": "",
                                 "radio_depend_on_private_information": ""}

        new_epsilon_questions = {"secret_sample": "",
                                 "population_size": "7000",
                                 "observations_number_can_be_public": ''}

        update_payload = dict(dataset_questions=new_dataset_questions,
                              epsilon_questions=new_epsilon_questions,
                              wizard_step='step_300')

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        # print(update_resp.json())

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['epsilon_questions'], new_epsilon_questions)
        self.assertEqual(update_resp_json['dataset_questions'], new_dataset_questions)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED))

        # (4) Update depositor info: default_epsilon, epsilon
        #
        new_variable_info = json.load(open(join(FIXTURE_DATA_DIR, 'test_data_profile_teacher_survey.json'), 'r'))

        update_payload = dict(variable_info=new_variable_info)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['variable_info'], new_variable_info)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED))

        # print('update_resp_json', update_resp_json)

        # (5) Update depositor info: default_epsilon, epsilon
        #
        depositor_setup_obj = DepositorSetupInfo.objects.get(object_id=setup_object_id)
        depositor_setup_obj.epsilon = 0.5
        depositor_setup_obj.delta = 0.00001
        depositor_setup_obj.save()

        new_epsilon = None
        new_delta = None

        update_payload = dict(epsilon=new_epsilon,
                              delta=new_delta)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        # print('update_resp.update_resp', update_resp.status_code)
        # print('update_resp.content', update_resp.content)
        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['delta'], new_delta)
        self.assertEqual(update_resp_json['epsilon'], new_epsilon)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED))

    def test_120_update_wizard_step(self):
        """(120) Test wizard step updates"""
        msgt(self.test_120_update_wizard_step.__doc__)

        # (1) Upload a file
        #
        jresp = self.upload_file_via_api()

        # (2) Get the dataset info
        #
        ds_object_id = jresp['object_id']
        ds_info = self.get_dataset_info_via_api(ds_object_id)
        # print('ds_info', ds_info)

        setup_object_id = ds_info['depositor_setup_info']['object_id']

        partial_update_url = f'{self.API_DEPOSIT}{setup_object_id}/'

        # --------------------------------------------
        # (3) Update wizard step 1: success
        # --------------------------------------------
        new_wizard_step = 'step_400'
        update_payload = dict(wizard_step=new_wizard_step)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        # print(update_resp.json())
        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['wizard_step'], new_wizard_step)
        self.assertEqual(update_resp_json['is_complete'], False)

        # --------------------------------------------
        # (4) Update wizard step 2: success
        # --------------------------------------------
        new_wizard_step2 = 'step_200'
        update_payload = dict(wizard_step=new_wizard_step2)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        # print(update_resp.json())
        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['wizard_step'], new_wizard_step2)
        self.assertEqual(update_resp_json['is_complete'], False)

        # --------------------------------------------
        # (5) Update wizard step 4: success
        # --------------------------------------------
        new_wizard_step_number = 100
        update_payload = dict(wizard_step=new_wizard_step_number)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        # print(update_resp.json())
        self.assertEqual(update_resp.status_code, HTTPStatus.OK)
        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['wizard_step'], str(new_wizard_step_number))

    def test_130_epsilon_question(self):
        """
        (130) Test population sample question--an epsilon question.
        Updated to allow population_size to be empty. Some test are redundant with
        test_file_upload.py: test_060_epsilon_question_validator
        """
        msgt(self.test_130_epsilon_question.__doc__)

        # (1) Upload a file
        #
        jresp = self.upload_file_via_api()

        # (2) Get the dataset info
        #
        ds_object_id = jresp['object_id']
        ds_info = self.get_dataset_info_via_api(ds_object_id)

        # --------------------------------------------
        # (3) Epsilon questions, secret_sample is "yes", but population_size is empty -- which is okay
        # --------------------------------------------
        setup_object_id = ds_info['depositor_setup_info']['object_id']

        partial_update_url = f'{self.API_DEPOSIT}{setup_object_id}/'

        new_epsilon_questions = {"secret_sample": "yes",
                                 "population_size": "",
                                 "observations_number_can_be_public": ''}

        update_payload = dict(epsilon_questions=new_epsilon_questions)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['epsilon_questions'], new_epsilon_questions)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED))

        # --------------------------------------------
        # (4) Epsilon questions, secret_sample is "yes",
        #   but population_size is a string
        # --------------------------------------------
        new_epsilon_questions = {"secret_sample": "yes",
                                 "population_size": "9000",
                                 "observations_number_can_be_public": ''}

        update_payload = dict(epsilon_questions=new_epsilon_questions)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.BAD_REQUEST)

        update_resp_json = update_resp.json()

        expected_err = astatic.ERR_MSG_POPULATION_SIZE_MISSING.format(val_type=str)
        self.assertEqual(update_resp_json['epsilon_questions'][0], expected_err)

        # --------------------------------------------
        # (5) Epsilon questions, secret_sample is "yes",
        #   but population_size is negative
        # --------------------------------------------
        new_epsilon_questions = {"secret_sample": "yes",
                                 "population_size": -9000,
                                 "observations_number_can_be_public": ''}

        update_payload = dict(epsilon_questions=new_epsilon_questions)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.BAD_REQUEST)

        update_resp_json = update_resp.json()

        expected_err = astatic.ERR_MSG_POPULATION_CANNOT_BE_NEGATIVE.format(pop_size=-9000)
        self.assertEqual(update_resp_json['epsilon_questions'][0], expected_err)

        # --------------------------------------------
        # (6) Epsilon questions, secret_sample is "yes" and population_size is positive
        # --------------------------------------------
        setup_object_id = ds_info['depositor_setup_info']['object_id']

        partial_update_url = f'{self.API_DEPOSIT}{setup_object_id}/'

        new_epsilon_questions = {"secret_sample": "yes",
                                 "population_size": 17000,
                                 "observations_number_can_be_public": ''}

        update_payload = dict(epsilon_questions=new_epsilon_questions)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['epsilon_questions'], new_epsilon_questions)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED))

    def test_140_dataset_question(self):
        """(140) Test dataset question -- troubleshooting"""
        msgt(self.test_140_dataset_question.__doc__)

        # (1) Upload a file
        #
        jresp = self.upload_file_via_api()

        # (2) Get the dataset info
        #
        ds_object_id = jresp['object_id']
        ds_info = self.get_dataset_info_via_api(ds_object_id)

        # --------------------------------------------
        # (3) Epsilon questions, secret_sample is "yes", but population_size is empty -- which is okay
        # --------------------------------------------
        setup_object_id = ds_info['depositor_setup_info']['object_id']

        partial_update_url = f'{self.API_DEPOSIT}{setup_object_id}/'

        update_payload = {
            "dataset_questions": {
                "radio_depend_on_private_information": "yes",
                "radio_best_describes": "",
                "radio_only_one_individual_per_row": ""
            },
            "default_epsilon": None,
            "default_delta": None,
            "epsilon": None,
            "delta": None
        }

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        # print('update_resp_json', update_resp.json())
        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['dataset_questions'], update_payload['dataset_questions'])
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED))

        # Try "is_complete" update, should fail
        #
        update_resp = self.client.patch(partial_update_url,
                                        data=dict(is_complete=True),
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(update_resp.json()['message'],
                         dstatic.ERR_MSG_COMPLETE_NOT_ALLOWED_INVALID_DATA)

    def test_150_update_depositor_info_api(self):
        """(150) Test update depositor info, default fields"""
        msgt(self.test_150_update_depositor_info_api.__doc__)

        # (1) Upload a file
        #
        jresp = self.upload_file_via_api()

        # (2) Get the dataset info
        #
        ds_object_id = jresp['object_id']
        ds_info = self.get_dataset_info_via_api(ds_object_id)
        # print('ds_info', ds_info)

        # (3) Update depositor info: epsilon questions, dataset_questions
        #
        setup_object_id = ds_info['depositor_setup_info']['object_id']

        partial_update_url = f'{self.API_DEPOSIT}{setup_object_id}/'

        new_epsilon_questions = {"secret_sample": "no",
                                 "population_size": "not applicable",
                                 "observations_number_can_be_public": "no"}

        new_dataset_questions = {"radio_best_describes": "notHarmButConfidential",
                                 "radio_only_one_individual_per_row": "yes",
                                 "radio_depend_on_private_information": "yes"}

        update_payload = dict(epsilon_questions=new_epsilon_questions,
                              dataset_questions=new_dataset_questions)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['epsilon_questions'], new_epsilon_questions)
        self.assertEqual(update_resp_json['dataset_questions'], new_dataset_questions)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0200_VALIDATED))

        # (4) Update depositor info: default_epsilon, epsilon
        #
        new_variable_info = json.load(open(join(FIXTURE_DATA_DIR,
                                                'test_data_profile_teacher_survey.json'), 'r'))

        update_payload = dict(variable_info=new_variable_info)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['variable_info'], new_variable_info)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE))

        # print('update_resp_json', update_resp_json)

        # (5) Update depositor info: default_epsilon, epsilon
        #
        new_default_epsilon = 0.5
        new_epsilon = 0.75

        update_payload = dict(default_epsilon=new_default_epsilon,
                              epsilon=new_epsilon)

        update_resp = self.client.patch(partial_update_url,
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['default_epsilon'], 1.0)  # set via dataset_questions
        self.assertEqual(update_resp_json['default_delta'], astatic.DELTA_10_NEG_5)  # set via dataset_questions

        self.assertEqual(update_resp_json['epsilon'], new_epsilon)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0600_EPSILON_SET))

    def test_160_update_is_complete(self):
        """(160) Test update depositor info, default fields"""
        msgt(self.test_160_update_is_complete.__doc__)

        ds_info = self.upload_file_via_api()
        self.assertTrue('object_id' in ds_info)

        setup_info = self.get_depositor_setup_info_via_api(ds_info['object_id'])

        self.populate_depositor_setup_info(setup_info)

        # (1) Setting "is_complete" to True should work
        #
        update_payload = {"is_complete": True,
                          "wizard_step": "Jessie Mae Hemphill"}

        update_resp = self.client.patch(f'{self.API_DEPOSIT}{setup_info.object_id}/',
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], update_payload['is_complete'])
        self.assertEqual(update_resp_json['wizard_step'], update_payload['wizard_step'])

        # (2) Setting "is_complete" a 2nd time should fail
        #
        update_payload = {"is_complete": True}

        update_resp = self.client.patch(f'{self.API_DEPOSIT}{setup_info.object_id}/',
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.BAD_REQUEST)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['message'], dstatic.ERR_MSG_ONLY_WIZARD_ALREADY_COMPLETE)

        # (3) Setting "wizard_step" should still work
        #
        update_payload = {dstatic.KEY_WIZARD_STEP: 'west savannah'}

        update_resp = self.client.patch(f'{self.API_DEPOSIT}{setup_info.object_id}/',
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp.json()['wizard_step'], update_payload['wizard_step'])
        self.assertEqual(update_resp.json()['is_complete'], True)
        self.assertEqual(update_resp.json()['object_id'], str(setup_info.object_id))

    def test_170_update_is_complete_fail(self):
        """(170) Test update depositor info, default fields"""
        msgt(self.test_170_update_is_complete_fail.__doc__)

        ds_info = self.upload_file_via_api()
        self.assertTrue('object_id' in ds_info)

        setup_info = self.get_depositor_setup_info_via_api(ds_info['object_id'])

        self.populate_depositor_setup_info(setup_info)

        # (1) Setting "is_complete" to True should fail, b/c of additional data
        #
        update_payload = {"is_complete": True,
                          "epsilon": 2.5}

        update_resp = self.client.patch(f'{self.API_DEPOSIT}{setup_info.object_id}/',
                                        data=update_payload,
                                        content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.BAD_REQUEST)

        key_list_str = 'is_complete, epsilon'
        user_msg = dstatic.ERR_MSG_ONLY_WIZARD_STEP_MAY_BE_UPDATED.format(key_list_str=key_list_str)
        self.assertEqual(update_resp.json()['message'], user_msg)
