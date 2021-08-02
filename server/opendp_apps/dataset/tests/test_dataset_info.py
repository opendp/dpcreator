import requests_mock

from django.contrib.auth import get_user_model
from django.urls import reverse

from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest
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

    def test_successful_patch(self, req_mocker):
        """(10) Successful patch"""
        msgt(self.test_successful_patch.__doc__)
        self.set_mock_requests(req_mocker)
        response = self.client.patch(reverse("deposit-detail",
                                             kwargs={'object_id': "9255c067-e435-43bd-8af1-33a6987ffc9b"}), {})
        self.assertEqual(response.status_code, 200)
        # print(response.json())
        response = response.json()
        response.pop('updated')
        self.assertEqual(response,
                         {'id': 1, 'creator': 1, 'created': '2021-03-23T17:22:50.889000Z',
                          'object_id': '9255c067-e435-43bd-8af1-33a6987ffc9b',
                          'is_complete': False, 'user_step': 'step_100', 'epsilon': None,
                          'dataset_questions': None, 'variable_info': None})

    def test_unsuccessful_patch(self, req_mocker):
        msgt(self.test_unsuccessful_patch.__doc__)
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
