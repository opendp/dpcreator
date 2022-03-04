from unittest import skip
import uuid

import requests_mock

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status as http_status

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import ManifestTestParams, DataverseHandoff
from opendp_apps.model_helpers.msg_util import msg, msgt
from opendp_apps.user.models import OpenDPUser, DataverseUser
from opendp_apps.user.dataverse_user_initializer import DataverseUserInitializer
from rest_framework.authtoken.models import TokenProxy


@requests_mock.Mocker()
@override_settings(ACCOUNT_EMAIL_VERIFICATION='none') # 'mandatory'
class TestDataverseHandoffView(TestCase):
    """
    Should redirect to home in both cases, but with params
    in case of successful DataverseHandoff creation
    """

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                'test_dv_handoff_rp_01.json']

    def setUp(self):
        # test client
        self.client = APIClient()

        self.registration_url = '/rest-auth/registration/'

        self.signup_data = {"username":"a_user_name",
                            "password1":"Heyhey-20",
                            "password2":"Heyhey-20",
                            "email":"some_email@harvard-edu.com",
                            "handoffId":"7db30776-cd08-4b25-af4d-b5a42a84e3d9",
                           }
        # self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        # self.client.force_login(self.user_obj)
        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()
        return
        self.data = {
            # 'dv_installation': 'https://dataverse.harvard.edu',
            'user': '4472310a-f591-403a-b8d6-dfb562f8b32f',
            'dv_handoff': '9e7e5506-dd1a-4979-a2c1-ec6e59e4769c',
            'persistent_id': 1,
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test',
            dv_static.DV_API_GENERAL_TOKEN: 1234,
            # TODO: Repeated field, camelcase is for parent model field, snakecase is for serializer
            dv_static.DV_PARAM_SITE_URL: 'https://dataverse.harvard.edu',
            dv_static.DV_PARAM_FILE_ID: 1,
            dv_static.DV_PARAM_DATASET_PID: 'doi:10.7910/DVN/B7DHBK'
        }

    def set_mock_requests(self, req_mocker):
        """
        Set up test urls that are used by the requests library
        """
        #return
        # Server Info
        server_info = {dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK,
                       'data': {'message': 'dataverse.MOCK-SERVER.edu'}}
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/info/server', json=server_info)

        # User Info
        user_info = {dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK, 'data': self.mock_params.user_info}
        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/users/:me', json=user_info)

        # req_mocker.get('http://www.invalidsite.com/api/v1/users/:me')

        req_mocker.get('www.invalidsite.com/api/v1/users/:me')
        req_mocker.get('http://www.invalidsite.com/api/v1/users/:me')

        req_mocker.get('https://dataverse.harvard.edu/api/v1/users/:me', json=user_info)

    def test_10_register_handoff_is_none(self, req_mocker):
        """(10) Register w/ handoff id set to None"""
        msgt(self.test_10_register_handoff_is_none.__doc__)

        self.signup_data["handoffId"] = None

        response = self.client.post(self.registration_url,
                                    data=self.signup_data,
                                    format='json')

        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

        resp_json = response.json()
        self.assertTrue('key' in resp_json)

        # ref: https://github.com/encode/django-rest-framework/blob/master/rest_framework/authtoken/models.py#L43
        token_proxy = TokenProxy.objects.get(key=resp_json.get('key'))

        self.assertEqual(token_proxy.user.username, self.signup_data['username'])
        self.assertEqual(token_proxy.user.email, self.signup_data['email'])

        # No associated DataverseUser objects
        self.assertEqual(DataverseUser.objects.filter(user=token_proxy.user).count(), 0)

        # Try to register again with the same username, email
        #
        fail_resp = self.client.post(self.registration_url,
                                    data=self.signup_data,
                                    format='json')
        # print(fail_resp.status_code)
        # print(fail_resp.content)

        self.assertEqual(fail_resp.status_code, http_status.HTTP_400_BAD_REQUEST)
        resp_json2 = fail_resp.json()
        # Expected JSON response:
        #   {"username":["A user with that username already exists."],
        #    "email":["A user is already registered with this e-mail address."]}

        self.assertTrue('username' in resp_json2)
        self.assertTrue('email' in resp_json2)

        username_msg = 'A user with that username already exists.'
        self.assertEqual(resp_json2['username'][0], username_msg)

        email_msg = 'A user is already registered with this e-mail address.'
        self.assertEqual(resp_json2['email'][0], email_msg)

    def test_20_register_no_handoff(self, req_mocker):
        """(20) Register w/o a handoff id"""
        msgt(self.test_20_register_no_handoff.__doc__)

        del self.signup_data["handoffId"]

        response = self.client.post(self.registration_url,
                                    data=self.signup_data,
                                    format='json')

        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

        resp_json = response.json()
        self.assertTrue('key' in resp_json)

        # ref: https://github.com/encode/django-rest-framework/blob/master/rest_framework/authtoken/models.py#L43
        token_proxy = TokenProxy.objects.get(key=resp_json.get('key'))

        self.assertEqual(token_proxy.user.username, self.signup_data['username'])
        self.assertEqual(token_proxy.user.email, self.signup_data['email'])

        # No associated DataverseUser objects
        self.assertEqual(DataverseUser.objects.filter(user=token_proxy.user).count(), 0)

    def test_30_register_with_handoff(self, req_mocker):
        """(30) Register w/ a handoff id"""
        msgt(self.test_30_register_with_handoff.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        response = self.client.post(self.registration_url,
                                    data=self.signup_data,
                                    format='json')

        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

        resp_json = response.json()
        print(resp_json)
        self.assertTrue('key' in resp_json)

        # ref: https://github.com/encode/django-rest-framework/blob/master/rest_framework/authtoken/models.py#L43
        token_proxy = TokenProxy.objects.get(key=resp_json.get('key'))

        self.assertEqual(token_proxy.user.username, self.signup_data['username'])
        self.assertEqual(token_proxy.user.email, self.signup_data['email'])

        # One associated DataverseUser objects
        self.assertEqual(DataverseUser.objects.filter(user=token_proxy.user).count(), 1)

        # test params in test_manifest_params_04.json
        dv_user = DataverseUser.objects.get(user=token_proxy.user, email='mock_user@some.edu')
        self.assertIsNotNone(dv_user)
        self.assertEqual(dv_user.persistent_id, 'https://fed.some-it.some.edu/idp/shibboleth|92459eabc12ec34@some.edu')

    def test_40_register_bad_handoff(self, req_mocker):
        """(40) Register w/ a bad handoff id"""
        msgt(self.test_40_register_bad_handoff.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # handoff id w/ no corresponding object
        self.signup_data["handoffId"] = 'f776261c-0443-4d0d-98aa-f089e7728dc2'

        response = self.client.post(self.registration_url,
                                    data=self.signup_data,
                                    format='json')

        self.assertEqual(response.status_code, http_status.HTTP_400_BAD_REQUEST)

        resp_json = response.json()
        # expected response: {'handoffId': ['DataverseHandoff does not exist']}
        # print(resp_json)

        self.assertTrue('handoffId' in resp_json)
        self.assertTrue(len(resp_json['handoffId']), 1)
        self.assertEqual(resp_json['handoffId'][0], 'DataverseHandoff does not exist')

        self.assertEqual(DataverseUser.objects.count(), 0)


    @skip
    def test_20_blank_data_for_creation(self, req_mocker):
        """(20) test_blank_data_for_creation"""
        msgt(self.test_20_blank_data_for_creation.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-handoff-list')

        bad_data = {}
        response = self.client.post(url, data=bad_data, format='json')
        msg(response)
        # Ensure redirect
        self.assertEqual(response.status_code, 302)
        # Since no params passed, we expect them all to appear under error_code
        self.assertEqual(response.url, '/?error_code=site_url%2CfileId%2CdatasetPid%2CapiGeneralToken')

    @skip
    def test_30_invalid_site_url_for_creation(self, req_mocker):
        """(30) test_invalid_site_url_for_creation"""
        msgt(self.test_30_invalid_site_url_for_creation.__doc__)

        # set the mock requests
        self.set_mock_requests(req_mocker)

        # Now test the API call which would be initiated from the Vue.js client
        #
        url = reverse('dv-handoff-list')

        self.data[dv_static.DV_PARAM_SITE_URL] = 'https://invalidsite.com'
        response = self.client.post(url, data=self.data, format='json')
        msg(response)
        # Ensure redirect
        self.assertEqual(response.status_code, 302)
        # Other params are present and valid, so we should just see dv_installation here
        self.assertEqual(response.url, '/?error_code=site_url')
