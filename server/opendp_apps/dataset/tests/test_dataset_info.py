import requests_mock

from django.contrib.auth import get_user_model
from django.urls import reverse

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest
from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.utils.extra_validators import \
    VALIDATE_MSG_ZERO_OR_GREATER, VALIDATE_MSG_EPSILON
from opendp_apps.model_helpers.msg_util import msgt


@requests_mock.Mocker()
class TestDepositorInfo(BaseEndpointTest):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                'test_opendp_users_01.json',
                'test_dataset_data_001.json']

    def setUp(self) -> None:
        super(TestDepositorInfo, self).setUp()
        self.user_obj, _created = get_user_model().objects.get_or_create(pk=1)
        self.client.force_login(self.user_obj)

    def test_10_successful_patch(self, req_mocker):
        """(10) Successful patch"""
        msgt(self.test_10_successful_patch.__doc__)
        self.set_mock_requests(req_mocker)
        response = self.client.patch(reverse("deposit-detail",
                                             kwargs={'object_id': "9255c067-e435-43bd-8af1-33a6987ffc9b"}),
                                     {'default_epsilon': 1.0,
                                      'epsilon': 0.9,
                                      'default_delta': astatic.DELTA_0,
                                      'delta': astatic.DELTA_10_NEG_6,
                                      'confidence_level': astatic.CL_99})
        print('(10 resp)', response.json())
        self.assertEqual(response.status_code, 200)
        response = response.json()

        response.pop('updated')
        self.assertEqual(response,
                         {'id': 1,
                          'created': '2021-03-23T17:22:50.889000Z',
                          'object_id': '9255c067-e435-43bd-8af1-33a6987ffc9b',
                          'dataset_questions': None,
                          'dataset_size': None,
                          'epsilon_questions': None,
                          'is_complete': False,
                          'user_step': 'step_100',
                          'default_epsilon': 1.0,
                          'epsilon': 0.9,
                          'default_delta': astatic.DELTA_0,
                          'delta': astatic.DELTA_10_NEG_6,
                          'confidence_level': astatic.CL_99,
                          'variable_info': None})


    def test_20_patch_restricted_field(self, req_mocker):
        """Try to patch a field that isn't allowed"""
        msgt(self.test_20_patch_restricted_field.__doc__)
        self.set_mock_requests(req_mocker)
        response = self.client.patch(reverse("deposit-detail",
                                             kwargs={'object_id': "9255c067-e435-43bd-8af1-33a6987ffc9b"}),
                                     {"dataset_schema_info": {"something": "this should fail"}}, format='json')
        # print(f"patch response: {response.json()}")
        # get_response = self.client.get(reverse("deposit-detail",
        #                                        kwargs={'object_id': "9255c067-e435-43bd-8af1-33a6987ffc9b"}))
        # print(f"get response: {get_response.json()}")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'message': 'These fields are not updatable',
                                           'fields': ['dataset_schema_info']})


    def test_30_patch_bad_values(self, req_mocker):
        """(30) Attempt a patch with a invalid values for updateable fields"""
        msgt(self.test_30_patch_bad_values.__doc__)
        self.set_mock_requests(req_mocker)
        response = self.client.patch(reverse("deposit-detail",
                                             kwargs={'object_id': "9255c067-e435-43bd-8af1-33a6987ffc9b"}),
                                     {'confidence_level': 0.48,
                                      'default_epsilon': -2,
                                      'epsilon': 0.0001,
                                      'default_delta': -0.1,
                                      'delta': -3})

        self.assertEqual(response.status_code, 400)
        print(f"get response: {response.json()}")

        expected_msg = {'confidence_level': ['"0.48" is not a valid choice.'],
                        'default_delta': [VALIDATE_MSG_ZERO_OR_GREATER],
                        'delta': [VALIDATE_MSG_ZERO_OR_GREATER],
                        'default_epsilon': [VALIDATE_MSG_EPSILON],
                        'epsilon': [VALIDATE_MSG_EPSILON]
                        }
        self.assertEqual(response.json(), expected_msg)
