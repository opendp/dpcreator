import json
import uuid
from http import HTTPStatus
from os.path import abspath, dirname, join

from django.core.exceptions import ValidationError
from django.urls import reverse

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataset.models import DepositorSetupInfo
from opendp_apps.dataset.tests.dataset_test_base import DatasetTestBase
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils.extra_validators import VALIDATE_MSG_EPSILON

CURRENT_DIR = dirname(abspath(__file__))
FIXTURE_DATA_DIR = join(dirname(CURRENT_DIR), 'fixtures')
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class TestFileUpload(DatasetTestBase):
    maxDiff = None

    def setUp(self):
        super().setUp()

    def test_010_file_upload_api(self):
        """(10) Test File Upload API"""
        msgt(self.test_010_file_upload_api.__doc__)

        self.upload_file_via_api()
        return

    def test_020_file_upload_bad_user_id(self):
        """(20) Test File Upload API - bad user id"""
        msgt(self.test_020_file_upload_bad_user_id.__doc__)

        bad_user_id = uuid.uuid4()

        payload = dict(name=self.upload_name,
                       creator=bad_user_id,
                       source_file=self.test_file_obj)

        upload_url = reverse("direct-upload-list")

        resp = self.client.post(upload_url,
                                data=payload)

        # print('resp', resp.json())
        # print('status code', resp.status_code)

        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)

        """
        Expected response: {'creator': 
            ['Object with object_id=a936f43f-e90a-4584-8f3e-4f03d5f1f704 does not exist.']}
        """
        jresp = resp.json()
        self.assertTrue('creator' in jresp)
        self.assertTrue(jresp['creator'][0].find('does not exist') > -1)

    def test_030_file_upload_delete(self):
        """(30) Create a file upload and then delete it via the API"""
        msgt(self.test_030_file_upload_delete.__doc__)

        payload = dict(name=self.upload_name,
                       creator=self.user_obj.object_id,
                       source_file=self.test_file_obj)

        resp = self.client.post(self.API_DIRECT_UPLOAD,
                                data=payload)

        object_id = resp.json().get('object_id')

        response = self.client.delete(f'{self.API_DIRECT_UPLOAD}{object_id}/')
        self.assertEqual(response.status_code, 204)

    def test_035_file_upload_retrieve(self):
        """(35) Retrieve a file upload"""
        msgt(self.test_035_file_upload_retrieve.__doc__)

        payload = dict(name=self.upload_name,
                       creator=self.user_obj.object_id,
                       source_file=self.test_file_obj)

        resp = self.client.post(self.API_DIRECT_UPLOAD,
                                data=payload)

        object_id = resp.json().get('object_id')

        response = self.client.get(f'{self.API_DATASET_INFO}{object_id}/')
        # response = self.client.get(f'{self.API_DATASET_INFO}')

        self.assertEqual(response.status_code, 200)

        response = self.client.delete(f'{self.API_DATASET_INFO}{object_id}/')
        print(response.status_code)
        self.assertEqual(response.status_code, 204)

    def test_040_update_depositor_info_api(self):
        """(40) Test update depositor info"""
        msgt(self.test_040_update_depositor_info_api.__doc__)

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

        # Note "is_complete" won't update b/c internal data
        # also needs to be in a
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

        # "is_complete" will work b/c data in a correct state
        #
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

    def test_060_epsilon_question_validator(self):
        """(60) Test epsilon question serializer"""
        msgt(self.test_060_epsilon_question_validator.__doc__)

        ds_info_json = self.upload_file_via_api()
        # print('ds_info_json', ds_info_json)
        depositor_info = self.get_depositor_setup_info_via_api(ds_info_json['object_id'])

        # (a) Trigger validation error for:
        #   - invalid population size
        #   - invalid epsilon
        #
        new_epsilon_questions = {"secret_sample": "yes",
                                 "population_size": -7000,
                                 astatic.SETUP_Q_05_ATTR: "no"}

        depositor_info.epsilon_questions = new_epsilon_questions
        depositor_info.epsilon = -1.0

        with self.assertRaises(ValidationError) as context:
            depositor_info.full_clean()
        err_dict = context.exception.error_dict

        self.assertTrue('epsilon_questions' in err_dict)
        self.assertEqual(err_dict['epsilon_questions'][0].message,
                         astatic.ERR_MSG_POPULATION_CANNOT_BE_NEGATIVE.format(pop_size=-7000))

        self.assertTrue('epsilon' in err_dict)
        self.assertEqual(err_dict['epsilon'][0].message, VALIDATE_MSG_EPSILON)

        # (b) Trigger validation error for:
        #   - invalid "yes" or "no" value
        #
        depositor_info = self.get_depositor_setup_info_via_api(ds_info_json['object_id'])

        _bad_val_yes_or_no = "should-be-yes-or-no"
        depositor_info.epsilon_questions = {astatic.SETUP_Q_05_ATTR: _bad_val_yes_or_no}

        with self.assertRaises(ValidationError) as context:
            depositor_info.full_clean()
        err_dict = context.exception.error_dict

        self.assertTrue('epsilon_questions' in err_dict)

        _expected_err = astatic.ERR_MSG_DATASET_YES_NO_QUESTIONS_INVALID_VALUE.format(
            key=astatic.SETUP_Q_05_ATTR,
            value=_bad_val_yes_or_no)
        self.assertEqual(err_dict['epsilon_questions'][0].message, _expected_err)

        # (c) Trigger validation error for:
        #   - Unknown attribute
        #
        depositor_info = self.get_depositor_setup_info_via_api(ds_info_json['object_id'])
        depositor_info.epsilon_questions = {'unknown_attribute': 'why is it here?'}
        with self.assertRaises(ValidationError) as context:
            depositor_info.full_clean()

        err_dict = context.exception.error_dict
        self.assertTrue('epsilon_questions' in err_dict)

        _expected_err = astatic.ERR_MSG_DATASET_QUESTIONS_INVALID_KEY.format(key='unknown_attribute')
        self.assertEqual(err_dict['epsilon_questions'][0].message, _expected_err)

        # Make sure that NOT setting the "epsilon_questions" value IS valid:
        #   - epsilon_questions
        #
        possible_vals = [None, {}, '']
        for pval in possible_vals:
            depositor_info.epsilon_questions = pval
            try:
                depositor_info.full_clean()
            except ValidationError as _err_obj:
                user_msg = f'ValidationError raised when "epsilon_questions" set to "{pval}"'
                self.fail(user_msg)
