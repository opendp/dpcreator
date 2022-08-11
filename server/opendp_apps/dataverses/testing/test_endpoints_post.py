import requests_mock

from datetime import datetime, timedelta

from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.signed_url_handler import SignedUrlHandler
from opendp_apps.dataverses.testing.test_endpoints_base import BaseEndpointTest
from opendp_apps.model_helpers.msg_util import msg, msgt
from opendp_apps.user.models import DataverseUser


@requests_mock.Mocker()
class DataversePostTest(BaseEndpointTest):


    def get_signed_urls_test_payload(self) -> dict:
        """Return a test payload as a Python dict"""
        next_week = datetime.now() + timedelta(days=7)
        next_week_str = next_week.strftime('%Y-%m-%dT%H:%M:%S.%f')

        payload = {
            "apis": [
                {
                    "name": "userInfo",
                    "httpMethod": "GET",
                    "signedUrl": f"http://host.docker.internal:8089/api/users/:me?until={next_week_str}&user=dataverseAdmin&method=GET&token=bad3cbfff29bb2c3f8baa168dd20c86444c3a710195b9e25915eca4cc41791f84c5c3be08ec6a0a5f52573fa86876714d00e807c223572e143f92149525f29b2",
                    "timeOut": 10
                },
                {
                    "name": "schemaInfo",
                    "httpMethod": "GET",
                    "signedUrl": f"http://host.docker.internal:8089/api/datasets/export?exporter=schema.org&persistentId=doi:10.5072/FK2/FEWCXP&until={next_week_str}&user=dataverseAdmin&method=GET&token=1f3ec61c1fdf7cff9211861e4a988cdda12592b779c77d14eed78c51aa2c9be58ac1ea58189f5821dc59233a1455f3c9e8d5df9e338e00190401d7fcff914032",
                    "timeOut": 15
                },
                {
                    "name": "retrieveDataFile",
                    "httpMethod": "GET",
                    "signedUrl": f"http://host.docker.internal:8089/api/access/datafile/:persistentId/?persistentId=&until={next_week_str}&user=dataverseAdmin&method=GET&token=e56bf3c771d6c734bcb8c23b1c15a10ea2c1ffbbcf2d40dac0893a934ecc8ce99e081f2feef2a35a0c51b6fde06e86ab1cfb0cdc2fe67e2435dd27cadfde636a",
                    "timeOut": 30
                },
                {
                    "name": "depositDPReleaseFile",
                    "httpMethod": "POST",
                    "signedUrl": f"http://host.docker.internal:8089/api/access/datafile/4/auxiliary/dpJson/v1?until={next_week_str}&user=dataverseAdmin&method=POST&token=ee4de3814aee1bbca70e5b92f46de3168c90a7491d0292d52318b035cb4dd3bf26dc3a48979ced66434c2004ce9452747d4e4436961b5a28f3df0a8a083c24b0",
                    "timeOut": 2880
                }
            ]
        }

        return payload

    def test_10_successful_creation(self, req_mocker):
        """(10) test_successful_creation"""
        msgt(self.test_10_successful_creation.__doc__)

        # delete DataverseUser loaded via fixture
        DataverseUser.objects.get(object_id='4472310a-f591-403a-b8d6-dfb562f8b32f').delete()

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        response = self.client.post(self.dv_user_url, data=self.dv_user_api_input_01, format='json')
        # print(f'status/response: {response.status_code}/{response.content}')

        self.assertEqual(response.status_code, 201)

    def test_20_user_not_found(self, req_mocker):
        """(20) test_user_not_found"""
        msgt(self.test_20_user_not_found.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        data = self.dv_user_api_input_01
        data['user'] = '1234567a-f591-403a-b8d6-dfb562f8b32f'
        response = self.client.post(self.dv_user_url, data=self.dv_user_api_input_01, format='json')

        # print(f'status/response: {response.status_code}/{response.content}')
        self.assertEqual(response.status_code, 400)

    def test_30_dataverse_handoff_not_found(self, req_mocker):
        """(30) test_dataverse_handoff_not_found"""
        msgt(self.test_30_dataverse_handoff_not_found.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        data = self.dv_user_api_input_01
        # non-existent handoff id
        data['dv_handoff'] = '1234567a-f591-403a-b8d6-dfb562f8b32f'

        response = self.client.post(self.dv_user_url, data=data, format='json')
        msg(f'server response: {response.json()}')
        self.assertEqual(response.status_code, 400)

    def test_50_invalid_token(self, req_mocker):
        """(50) Test an invalid token"""
        msgt(self.test_50_invalid_token.__doc__)

        # set the mock requests
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/users/:me',
                       json=self.dv_user_invalid_token)

        # Now test the API call which would be initiated from the Vue.js client
        #
        dataverse_handoff = DataverseHandoff.objects.first()
        dataverse_handoff.apiGeneralToken = 'invalid_token_1234'
        dataverse_handoff.save()

        response = self.client.post(self.dv_user_url, data=self.dv_user_api_input_01, format='json')

        # msg(response.content)

        self.assertEqual(response.status_code, 400)

    def test_60_duplicate_dataverse_user(self, req_mocker):
        """(60) Attempt to add the same user twice"""
        msgt(self.test_60_duplicate_dataverse_user.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Ensure there are no DataverseUsers
        DataverseUser.objects.all().delete()
        initial_dv_user_count = DataverseUser.objects.count()

        # Call once to create DataverseUser
        response = self.client.post(self.dv_user_url, data=self.dv_user_api_input_01, format='json')
        msg(response.json())
        self.assertEqual(response.status_code, 201)
        dataverse_users_count = DataverseUser.objects.count()
        self.assertEqual(initial_dv_user_count + 1, dataverse_users_count)

        # Now make the same request, and demonstrate that it queried for DataverseUser
        # rather than creating another one
        response = self.client.post(self.dv_user_url, data=self.dv_user_api_input_01, format='json')
        msg(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dataverse_users_count, DataverseUser.objects.count())

    def test_70_dataverse_signed_urls(self, req_mocker):
        """(70) Valid signed urls"""
        msgt(self.test_70_dataverse_signed_urls.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Prepare Dataverse test data
        #
        signed_url_data = self.get_signed_urls_test_payload()
        # del signed_url_data['apis'][0]

        incoming_url = '/api/dv-handoff/init-connection/'  # reverse('init-connection')
        print('incoming_url', incoming_url)

        response = self.client.post(incoming_url, data=signed_url_data, format='json')

        print('response.status_code', response.status_code)
        print('response.data', response.data)

        msg(f'server response: {response.json()}')
        self.assertEqual(response.status_code, 200)
