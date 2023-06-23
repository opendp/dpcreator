import json
import uuid
from http import HTTPStatus
from os.path import abspath, dirname, join

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataset.models import DepositorSetupInfo
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.utils.extra_validators import VALIDATE_MSG_EPSILON

CURRENT_DIR = dirname(abspath(__file__))
FIXTURE_DATA_DIR = join(dirname(CURRENT_DIR), 'fixtures')
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')


class TestFileUpload(TestCase):
    maxDiff = None

    def setUp(self):
        self.user_obj, _created = get_user_model().objects.get_or_create(username='rp')

        self.test_file_name = join('teacher_survey', 'teacher_survey.csv')
        self.upload_name = 'Teacher Survey'

        test_file = join(TEST_DATA_DIR, self.test_file_name)
        self.test_file_obj = SimpleUploadedFile(self.test_file_name,
                                                open(test_file, 'rb').read(),
                                                content_type="text/comma-separated-values")

        self.client.force_login(self.user_obj)

    def upload_file_via_api(self):
        """Convenience method to upload a file and return the response"""
        payload = dict(name=self.upload_name,
                       creator=self.user_obj.object_id,
                       source_file=self.test_file_obj)

        upload_url = '/api/direct-upload/'  # reverse("direct-upload-create")

        resp = self.client.post(upload_url,
                                data=payload)

        print('resp', resp.json())
        print('status code', resp.status_code)

        self.assertEqual(resp.status_code, HTTPStatus.CREATED)

        jresp = resp.json()
        self.assertEqual(jresp['creator'], str(self.user_obj.object_id))
        self.assertEqual(jresp['name'], self.upload_name)

        return jresp

    def get_dataset_info_via_api(self, dataset_object_id: str) -> dict:
        """Convenience method to get a dataset info object via the API"""
        assert dataset_object_id, "dataset_object_id cannot be None"

        dataset_info_url = f'/api/dataset-info/{dataset_object_id}/'
        resp = self.client.get(dataset_info_url)

        jresp = resp.json()
        self.assertTrue('depositor_setup_info' in jresp)
        self.assertTrue('object_id' in jresp['depositor_setup_info'])

        self.assertEqual(jresp['depositor_setup_info']['is_complete'], False)
        self.assertEqual(jresp['depositor_setup_info']['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0100_UPLOADED))

        return jresp

    def get_depositor_setup_info_via_api(self, dataset_object_id: str) -> DepositorSetupInfo:
        """Convenience method to get a depositor info object via the API"""
        assert dataset_object_id, "dataset_object_id cannot be None"

        setup_info_url = f'/api/dataset-info/{dataset_object_id}/'
        resp = self.client.get(setup_info_url)

        jresp = resp.json()
        self.assertTrue('depositor_setup_info' in jresp)
        self.assertTrue('object_id' in jresp['depositor_setup_info'])

        return DepositorSetupInfo.objects.get(object_id=jresp['depositor_setup_info']['object_id'])

    def test_10_file_upload_api(self):
        """(10) Test File Upload API"""
        msgt(self.test_10_file_upload_api.__doc__)

        self.upload_file_via_api()
        return

    def test_20_file_upload_bad_user_id(self):
        """(20) Test File Upload API - bad user id"""
        msgt(self.test_20_file_upload_bad_user_id.__doc__)

        bad_user_id = uuid.uuid4()

        payload = dict(name=self.upload_name,
                       creator=bad_user_id,
                       source_file=self.test_file_obj)

        upload_url = reverse("direct-upload-list")

        resp = self.client.post(upload_url,
                                data=payload)

        print('resp', resp.json())
        print('status code', resp.status_code)

        self.assertEqual(resp.status_code, HTTPStatus.BAD_REQUEST)

        """
        Expected response: {'creator': 
            ['Object with object_id=a936f43f-e90a-4584-8f3e-4f03d5f1f704 does not exist.']}
        """
        jresp = resp.json()
        self.assertTrue('creator' in jresp)
        self.assertTrue(jresp['creator'][0].find('does not exist') > -1)

    def test_30_file_upload_delete(self):
        """(30) Create a file upload and then delete it via the API"""
        msgt(self.test_30_file_upload_delete.__doc__)

        payload = dict(name=self.upload_name,
                       creator=self.user_obj.object_id,
                       source_file=self.test_file_obj)

        direct_upload_url = '/api/direct-upload/'

        resp = self.client.post(direct_upload_url,
                                data=payload)
        object_id = resp.json().get('object_id')
        response = self.client.delete(f'{direct_upload_url}{object_id}/')
        self.assertEqual(response.status_code, 204)

    def test_40_update_depositor_info_api(self):
        """(40) Test update depositor info"""
        msgt(self.test_40_update_depositor_info_api.__doc__)

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

        partial_update_url = f'/api/deposit/{setup_object_id}/'

        new_epsilon_questions = {"secret_sample": "no",
                                 "population_size": "not applicable",
                                 "observations_number_can_be_public": "no"}

        new_dataset_questions = {"radio_best_describes": "notHarmButConfidential",
                                 "radio_only_one_individual_per_row": "yes",
                                 "radio_depend_on_private_information": "yes"}

        update_payload = dict(epsilon_questions=new_epsilon_questions,
                              dataset_questions=new_dataset_questions)
        update_resp = self.client.put(partial_update_url,
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
        new_data_profile = json.load(open(join(FIXTURE_DATA_DIR, 'test_data_profile_teacher_survey.json'), 'r'))

        update_payload = dict(data_profile=new_data_profile)

        update_resp = self.client.put(partial_update_url,
                                      data=update_payload,
                                      content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['data_profile'], new_data_profile)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE))

        # print('update_resp_json', update_resp_json)

        # (5) Update depositor info: default_epsilon, epsilon
        #
        new_default_epsilon = 0.5
        new_epsilon = 0.75

        update_payload = dict(default_epsilon=new_default_epsilon,
                              epsilon=new_epsilon)

        update_resp = self.client.put(partial_update_url,
                                      data=update_payload,
                                      content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], True)
        self.assertEqual(update_resp_json['default_epsilon'], new_default_epsilon)
        self.assertEqual(update_resp_json['epsilon'], new_epsilon)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0600_EPSILON_SET))

    def test_60_epsilon_question_validator(self):
        """(60) Test epsilon question serializer"""
        msgt(self.test_60_epsilon_question_validator.__doc__)

        ds_info_json = self.upload_file_via_api()
        print('ds_info_json', ds_info_json)
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

    def test_70_update_depositor_info(self):
        """(70) Update depositor info including epsilon questions, dataset questions,
            epsilon, delta, etc."""
        msgt(self.test_70_update_depositor_info.__doc__)

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

        partial_update_url = f'/api/deposit/{setup_object_id}/'

        new_epsilon_questions = {"secret_sample": "no",
                                 "population_size": "7000",
                                 "observations_number_can_be_public": ''}

        new_dataset_questions = {"radio_best_describes": "notHarmButConfidential",
                                 "radio_only_one_individual_per_row": "",
                                 "radio_depend_on_private_information": "yes"}

        update_payload = dict(epsilon_questions=new_epsilon_questions,
                              dataset_questions=new_dataset_questions)
        update_resp = self.client.put(partial_update_url,
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
        
        # (4) Update depositor info: default_epsilon, epsilon
        #
        new_data_profile = json.load(open(join(FIXTURE_DATA_DIR, 'test_data_profile_teacher_survey.json'), 'r'))

        update_payload = dict(data_profile=new_data_profile)

        update_resp = self.client.put(partial_update_url,
                                      data=update_payload,
                                      content_type="application/json")

        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], False)
        self.assertEqual(update_resp_json['data_profile'], new_data_profile)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE))

        # print('update_resp_json', update_resp_json)

        # (5) Update depositor info: default_epsilon, epsilon
        #
        new_default_epsilon = 0.5
        new_epsilon = 0.75

        update_payload = dict(default_epsilon=new_default_epsilon,
                              epsilon=new_epsilon)

        update_resp = self.client.put(partial_update_url,
                                      data=update_payload,
                                      content_type="application/json")

        print('update_resp.update_resp', update_resp.status_code)
        print('update_resp.content', update_resp.content)
        self.assertEqual(update_resp.status_code, HTTPStatus.OK)

        update_resp_json = update_resp.json()
        self.assertEqual(update_resp_json['is_complete'], True)
        self.assertEqual(update_resp_json['default_epsilon'], new_default_epsilon)
        self.assertEqual(update_resp_json['epsilon'], new_epsilon)
        self.assertEqual(update_resp_json['user_step'],
                         str(DepositorSetupInfo.DepositorSteps.STEP_0600_EPSILON_SET))

        print(json.dumps(update_resp_json, indent=4))