"""
For more context regarding these tests, please see the document:
- /server/opendp_apps/user/README.md
"""
from unittest import skip

import requests_mock

from django.test import TestCase, override_settings

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
@override_settings(ACCOUNT_EMAIL_VERIFICATION='none')  # 'mandatory'
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

        self.test_handoff_id = "7db30776-cd08-4b25-af4d-b5a42a84e3d9"

        self.signup_data = {"username": "a_user_name",
                            "password1": "Heyhey-20",
                            "password2": "Heyhey-20",
                            "email": "some_email@harvard-edu.com",
                            "handoffId": self.test_handoff_id}

        self.login_url = '/rest-auth/login/'

        self.login_data = dict(username=self.signup_data['username'],
                               password=self.signup_data['password1'])

        # self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

        # self.client.force_login(self.user_obj)
        self.mock_params = ManifestTestParams.objects.filter(use_mock_dv_api=True).first()

    def set_mock_requests(self, req_mocker):
        """
        Set up test urls that are used by the requests library
        """
        # Server Info
        server_info = {dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK,
                       'data': {'message': 'dataverse.MOCK-SERVER.edu'}}

        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/info/server',
                       json=server_info)

        # User Info
        user_info = {dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK,
                     'data': self.mock_params.user_info}

        req_mocker.get('http://127.0.0.1:8000/dv-mock-api/api/v1/users/:me',
                       json=user_info)

        # req_mocker.get('http://www.invalidsite.com/api/v1/users/:me')
        # req_mocker.get('www.invalidsite.com/api/v1/users/:me')
        # req_mocker.get('http://www.invalidsite.com/api/v1/users/:me')

        req_mocker.get('https://dataverse.harvard.edu/api/v1/users/:me',
                       json=user_info)

    def setup_register_user(self, handoff_id=None):
        """Register user as a setup"""
        self.signup_data["handoffId"] = handoff_id

        response = self.client.post(self.registration_url,
                                    data=self.signup_data,
                                    format='json')

        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

        resp_json = response.json()

        # Should contain a key to a TokenProxy object
        # ref: https://github.com/encode/django-rest-framework/blob/master/rest_framework/authtoken/models.py#L43
        #
        self.assertTrue('key' in resp_json)

        # Retrieve the OpenDP user and check that the username and email match
        #
        token_proxy = TokenProxy.objects.get(key=resp_json.get('key'))

        self.assertEqual(token_proxy.user.username, self.signup_data['username'])
        self.assertEqual(token_proxy.user.email, self.signup_data['email'])

        return token_proxy.user  # return the OpenDP User

    def test_10_register_handoff_is_none(self, _req_mocker):
        """(10) Register w/ handoff id set to None"""
        msgt(self.test_10_register_handoff_is_none.__doc__)

        opendp_user = self.setup_register_user(handoff_id=None)

        # No associated DataverseUser objects
        self.assertEqual(DataverseUser.objects.filter(user=opendp_user).count(), 0)

        # Try to register again with the same username, email
        #
        fail_resp = self.client.post(self.registration_url,
                                     data=self.signup_data,
                                     format='json')

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

        opendp_user = self.setup_register_user(handoff_id=self.test_handoff_id)

        """
        response = self.client.post(self.registration_url,
                                    data=self.signup_data,
                                    format='json')

        self.assertEqual(response.status_code, http_status.HTTP_201_CREATED)

        
        resp_json = response.json()
        print(resp_json)
        # ref: https://github.com/encode/django-rest-framework/blob/master/rest_framework/authtoken/models.py#L43

        # Retrieve the OpenDP user and check that the username and email match
        #
        token_proxy = TokenProxy.objects.get(key=resp_json.get('key'))

        self.assertEqual(token_proxy.user.username, self.signup_data['username'])
        self.assertEqual(token_proxy.user.email, self.signup_data['email'])
        """
        # Check that the handoff id is attached to the user object
        #
        self.assertEqual(str(opendp_user.handoff_id), self.test_handoff_id)

        # One associated DataverseUser objects
        self.assertEqual(DataverseUser.objects.filter(user=opendp_user).count(), 1)

        # test params in test_manifest_params_04.json
        dv_user = DataverseUser.objects.get(user=opendp_user, email='mock_user@some.edu')
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

        # Check the error message. Should be: 'DataverseHandoff does not exist'
        resp_json = response.json()
        self.assertTrue('handoffId' in resp_json)
        self.assertEqual(resp_json['handoffId'][0], 'DataverseHandoff does not exist')

        self.assertEqual(DataverseUser.objects.count(), 0)

    def test_50_login(self, _req_mocker):
        """(50) Login"""
        msgt(self.test_50_login.__doc__)

        # Register a new user
        #
        self.setup_register_user(handoff_id=None)  # Create an OpenDPUser, without a DataversUser

        resp = self.client.post(self.login_url,
                                data=self.login_data,
                                format='json')

        # Should be a 200 status code
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)

        # Retrieve the user
        token_proxy = TokenProxy.objects.get(key=resp.json().get('key'))

        # Is the username we logged in with?
        self.assertEqual(token_proxy.user.username, self.login_data['username'])

    def test_60_login_handoff_on_opendp_user(self, req_mocker):
        """(60) Login and there's an existing handoff_id on the OpenDPUser
            - Register a new OpenDPUser
            - The OpenDPUser.handoff_id is populated
            - Login and retrieve the
        """
        msgt(self.test_60_login_handoff_on_opendp_user.__doc__)

        self.set_mock_requests(req_mocker)

        # Register a new user
        #
        reg_opendp_user = self.setup_register_user(handoff_id=self.test_handoff_id)

        self.assertEqual(str(reg_opendp_user.handoff_id), self.test_handoff_id)

        resp = self.client.post(self.login_url,
                                data=self.login_data,
                                format='json')

        # Should be a 200 status code
        self.assertEqual(resp.status_code, http_status.HTTP_200_OK)

        # Retrieve the user
        token_proxy = TokenProxy.objects.get(key=resp.json().get('key'))

        # Is the username we logged in with?
        self.assertEqual(token_proxy.user.username, self.login_data['username'])
        self.assertEqual(str(token_proxy.user.handoff_id), self.test_handoff_id)

        # Retrieve the DataverseHandoff object
        dv_handoff = DataverseHandoff.objects.filter(object_id=token_proxy.user.handoff_id).first()

        # Retrieve the DataverseUser object
        dv_user = DataverseUser.objects.filter(user=token_proxy.user,
                                               dv_installation=dv_handoff.dv_installation).first()
        self.assertTrue(dv_user is not None)

        # The logged in OpenDPUser and DataverseUser.user should be the same
        self.assertEqual(dv_user.user, token_proxy.user)

