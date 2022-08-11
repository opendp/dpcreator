import json

import requests_mock
from rest_framework.reverse import reverse

from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.testing.test_endpoints_base import BaseEndpointTest
from opendp_apps.model_helpers.msg_util import msg, msgt
from opendp_apps.user.models import DataverseUser


@requests_mock.Mocker()
class DataversePutTest(BaseEndpointTest):
    url = reverse('dv-user-detail', kwargs={'object_id': '4472310a-f591-403a-b8d6-dfb562f8b32f'})

    def test_10_successful_update(self, req_mocker):
        """(10) test_successful_update"""
        msgt(self.test_10_successful_update.__doc__)

        # ---------------------------
        # set the mock request
        # contains updated name, email, and persistentId
        # ---------------------------
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/users/:me',
                       json=self.dv_updated_user_info)

        # ---------------------------
        # Update the user
        # ---------------------------
        orig_user = DataverseUser.objects.get(pk=2)
        # url = reverse('dv-user-detail', kwargs={'pk': orig_user.object_id})
        # print('orig_user', orig_user, orig_user.id, orig_user.last_name, orig_user.first_name)

        response = self.client.put(self.url, data=self.dv_user_api_input_01, format='json')

        msg(response.content)

        json_resp = response.json()
        self.assertTrue(json_resp['success'])

        self.assertEqual(response.status_code, 200)

        updated_user = DataverseUser.objects.get(pk=1)
        # print('updated_user', updated_user, updated_user.id, updated_user.last_name, updated_user.first_name)
        self.assertNotEqual(orig_user.first_name, updated_user.first_name)
        self.assertNotEqual(orig_user.last_name, updated_user.last_name)
        self.assertNotEqual(orig_user.email, updated_user.email)
        self.assertNotEqual(orig_user.persistent_id, updated_user.persistent_id)

    def test_20_user_not_found(self, req_mocker):
        """(20) test_user_not_found"""
        msgt(self.test_20_user_not_found.__doc__)

        self.set_mock_requests(req_mocker)

        data = self.dv_user_api_input_01
        data['user'] = 0
        # Non-existent user object id
        url = reverse('dv-user-detail', kwargs={'object_id': '1234567a-f591-403a-b8d6-dfb562f8b32f'})

        response = self.client.put(url, data=data, format='json')
        msg(response.content)

        self.assertEqual(response.status_code, 400)

    def test_30_dataverse_handoff_not_found(self, req_mocker):
        """(30) test_dataverse_handoff_not_found"""
        msgt(self.test_30_dataverse_handoff_not_found.__doc__)

        self.set_mock_requests(req_mocker)

        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.site_url = 'www.invalidsite.com'
        dataverse_handoff.save()
        data = self.dv_user_api_input_01
        # Non-existent handoff object id
        data['dv_handoff'] = '1234567a-f591-403a-b8d6-dfb562f8b32f'

        response = self.client.put(self.url, data=data, format='json')
        msg(response.content)

        self.assertEqual(response.status_code, 400)

    def test_50_invalid_token(self, req_mocker):
        """(50) test_invalid_token"""
        msgt(self.test_50_invalid_token.__doc__)

        # set the mock requests
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/users/:me',
                       json=self.dv_user_invalid_token)

        # Now test the API call which would be initiated from the Vue.js client
        #
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.apiGeneralToken = 'invalid_token_1234'
        dataverse_handoff.save()

        response = self.client.put(self.url, data=self.dv_user_api_input_01, format='json')
        msg(response.content)

        self.assertEqual(response.status_code, 400)

        response_json = json.loads(response.content)
        self.assertTrue(response_json['success'] is False)
        self.assertTrue(response_json['message'].find('not found') > -1)
