from datetime import datetime, timedelta

import requests_mock

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.serializers import SignedUrlGroup, SingleSignedUrlSerializer
from opendp_apps.dataverses.testing.test_endpoints_base import BaseEndpointTest
from opendp_apps.model_helpers.msg_util import msg, msgt
from opendp_apps.user.models import DataverseUser
from opendp_apps.utils.format_errors import format_serializer_errors


@requests_mock.Mocker()
class DataversePostTest(BaseEndpointTest):

    def get_next_week_str(self, days=7) -> str:
        """
        Return a formatted string that is 7 days from the current time

        @param days:
        @return:
        """
        next_week = datetime.now() + timedelta(days=days)

        return next_week.strftime('%Y-%m-%dT%H:%M:%S.%f')

    def get_signed_urls_test_payload(self, days=7) -> dict:
        """Return a test payload as a Python dict"""
        next_week_str = self.get_next_week_str(days)

        payload = {
            "signedUrls": [
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
        # msg(response.json())
        self.assertEqual(response.status_code, 201)
        dataverse_users_count = DataverseUser.objects.count()
        self.assertEqual(initial_dv_user_count + 1, dataverse_users_count)

        # Now make the same request, and demonstrate that it queried for DataverseUser
        # rather than creating another one
        response = self.client.post(self.dv_user_url, data=self.dv_user_api_input_01, format='json')
        # msg(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(dataverse_users_count, DataverseUser.objects.count())

    def test_70_dataverse_signed_urls(self, _req_mocker):
        """(70) Valid signed urls"""
        msgt(self.test_70_dataverse_signed_urls.__doc__)

        # Looks good!
        signed_url_data = self.get_signed_urls_test_payload()
        serializer = SignedUrlGroup(data=signed_url_data)
        self.assertTrue(serializer.is_valid())

    def test_80_invalid_signed_urls(self, _req_mocker):
        """(80) Missing signed url"""
        msgt(self.test_80_invalid_signed_urls.__doc__)

        # One of the urls is missing
        signed_url_data = self.get_signed_urls_test_payload()
        del signed_url_data['signedUrls'][3]  # Delete the last url
        serializer = SignedUrlGroup(data=signed_url_data)
        self.assertFalse(serializer.is_valid())

        errors = format_serializer_errors(serializer.errors)
        self.assertTrue('signedUrls' in errors)
        self.assertTrue(errors['signedUrls'].find(dv_static.ERR_MSG_EXPECTED_4_SIGNED_URLS) > -1)

    def test_90_invalid_signed_url_params(self, _req_mocker):
        """(90) Invalid signed url params """
        msgt(self.test_90_invalid_signed_url_params.__doc__)

        # Bad name 'expressTrain'
        signed_url_data = self.get_signed_urls_test_payload()
        signed_url_data['signedUrls'][0]['name'] = 'expressTrain'  # Bad timeout value
        serializer = SignedUrlGroup(data=signed_url_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(str(serializer.errors).find('expressTrain') > -1)

        # Bad timeout value 'a'
        signed_url_data = self.get_signed_urls_test_payload()
        signed_url_data['signedUrls'][0]['timeOut'] = 'a'
        serializer = SignedUrlGroup(data=signed_url_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(str(serializer.errors).find('timeOut') > -1)

        # Bad timeout value -10
        signed_url_data = self.get_signed_urls_test_payload()
        signed_url_data['signedUrls'][0]['timeOut'] = -10  # Bad timeout value
        serializer = SignedUrlGroup(data=signed_url_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(str(serializer.errors).find('timeOut') > -1)

        # Bad httpMethod 'Hello'
        signed_url_data = self.get_signed_urls_test_payload()
        signed_url_data['signedUrls'][0]['httpMethod'] = 'Hello'  # Bad timeout value
        serializer = SignedUrlGroup(data=signed_url_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(str(serializer.errors).find('httpMethod') > -1)

    def test_100_expired_date_within_url(self, _req_mocker):
        """(100) Expired date within url """
        msgt(self.test_100_expired_date_within_url.__doc__)

        # Signed urls are expired
        signed_url_data = self.get_signed_urls_test_payload(-5)
        signed_url_data['signedUrls'][0]['name'] = 'blah'  # Also a bad name

        serializer = SignedUrlGroup(data=signed_url_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(str(serializer.errors).find('expired') > -1)
        self.assertTrue(str(serializer.errors).find('"blah" is not a valid choice') > -1)

    def test_110_invalid_date_within_url(self, _req_mocker):
        """(110) Invalid date within url """
        msgt(self.test_110_invalid_date_within_url.__doc__)

        # Expired url
        next_week_str = self.get_next_week_str(-2)
        url_data = dict(until=next_week_str,
                        user='dataverseAdmin',
                        method='GET',
                        token='bad3cbfff29bb2c3' * 10)
        serializer = SingleSignedUrlSerializer(data=url_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(str(serializer.errors).find('expired') > -1)

        # Invalid date within url
        url_data['until'] = self.get_next_week_str()[:10]  # date only. Example: 2022-08-22
        serializer = SingleSignedUrlSerializer(data=url_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue(str(serializer.errors).find(dv_static.ERR_MSG_BAD_DATETIME_STRING) > -1)

    def test_120_valid_signed_urls_via_api(self, req_mocker):
        """(120) Valid signedUrls via API"""
        msgt(self.test_120_valid_signed_urls_via_api.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Prepare Dataverse test data
        #
        signed_url_data = self.get_signed_urls_test_payload()

        incoming_url = '/api/dv-handoff/init-connection/'  # reverse('init-connection')

        response = self.client.post(incoming_url, data=signed_url_data, format='json')

        print('response.status_code', response.status_code)
        print('response.data', response.data)

        self.assertEqual(response.status_code, 200)

    def test_130_invalid_signed_urls_via_api(self, req_mocker):
        """(130) invalid signedUrls via API"""
        msgt(self.test_130_invalid_signed_urls_via_api.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Prepare Dataverse test data
        #
        signed_url_data = self.get_signed_urls_test_payload(days=-4)

        incoming_url = '/api/dv-handoff/init-connection/'  # reverse('init-connection')

        response = self.client.post(incoming_url, data=signed_url_data, format='json')

        print('response.status_code', response.status_code)
        print('response.data', response.data)

        self.assertEqual(response.status_code, 400)
