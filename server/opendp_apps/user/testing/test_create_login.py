"""
For more context regarding these tests, please see the document:
- /server/opendp_apps/user/README.md
"""

import requests_mock
from django.test import TestCase, override_settings
from rest_framework import status as http_status
from rest_framework.authtoken.models import TokenProxy
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import ManifestTestParams, DataverseHandoff
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.user.models import DataverseUser


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

        # connected to a DataverseHandoff object in the fixtures
        self.test_handoff_id = "7db30776-cd08-4b25-af4d-b5a42a84e3d9"

        # Not connected to a DataverseHandoff object
        self.bad_handoff_id = 'f776261c-0443-4d0d-98aa-f089e7728dc2'

        self.signup_data = {"username": "a_user_name",
                            "password1": "Heyhey-20",
                            "password2": "Heyhey-20",
                            "email": "some_email@harvard-edu.com",
                            "handoffId": self.test_handoff_id}

        self.login_url = '/rest-auth/login/'

        self.login_data = dict(username=self.signup_data['username'],
                               password=self.signup_data['password1'])

        self.dv_user_url = reverse('dv-user-list')  # '/api/dv-user/'

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
        self.signup_data["handoffId"] = self.bad_handoff_id

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

    def test_70_create_dv_user_post_registration(self, req_mocker):
        """(70) Rough imitation to the sequence for Social Auth login
        - Register a new OpenDPUser  (would be through Social Auth, OAuth)
        - Via the '/api/dv-user' endpoint, use the OpenDPUser id and handoff_id to create a DataverseUser
        - Use the same endpoint which should update the DV user (if needed) by making a call to the Dataverse API
        """
        msgt(self.test_70_create_dv_user_post_registration.__doc__)

        self.set_mock_requests(req_mocker)

        # Register a new user
        #
        reg_opendp_user = self.setup_register_user(handoff_id=None)
        self.assertEqual(str(reg_opendp_user.username), self.signup_data['username'])

        dv_user_data = dict(user=reg_opendp_user.object_id,
                            dv_handoff=self.test_handoff_id)

        print('dv_user_data', dv_user_data)
        resp = self.client.post(self.dv_user_url,
                                data=dv_user_data,
                                format='json')
        print('resp.status', resp.status_code)
        print('resp.content', resp.content)

        # Should be a 201 status code
        self.assertEqual(resp.status_code, http_status.HTTP_201_CREATED)

        # Example  {"success":true,
        #           "message":"success",
        #           "data":{"dv_user":"3807dd12-a2c2-43dc-ba4d-a373bef8760b"}}'
        #
        resp_json = resp.json()
        self.assertTrue(resp_json['success'] is True)
        self.assertTrue('dv_user' in resp_json['data'])
        dv_user_object_id = resp_json['data']['dv_user']

        # Make the same API call, it should be a 200, not a 201
        #
        resp_update = self.client.post(self.dv_user_url,
                                       data=dv_user_data,
                                       format='json')

        # print('resp_update.status', resp_update.status_code)
        # print('resp_update.content', resp_update.content)
        self.assertEqual(resp_update.status_code, http_status.HTTP_200_OK)

        resp_update_json = resp_update.json()
        self.assertTrue(resp_update_json['success'] is True)
        self.assertTrue('dv_user' in resp_update_json['data'])
        self.assertEqual(resp_update_json['data']['dv_user'], dv_user_object_id)

    def test_80_create_dv_user_post_registration_bad_handoff(self, req_mocker):
        """(80) Rough imitation to the sequence for Social Auth login, but with a bad handoff_id
        - Register a new OpenDPUser  (would be through Social Auth, OAuth)
        - Via the '/api/dv-user' endpoint, use the OpenDPUser id and handoff_id to create a DataverseUser
        - Should fail -- bad handoff id
        """
        msgt(self.test_80_create_dv_user_post_registration_bad_handoff.__doc__)

        self.set_mock_requests(req_mocker)

        # Register a new user
        #
        reg_opendp_user = self.setup_register_user(handoff_id=None)
        self.assertEqual(str(reg_opendp_user.username), self.signup_data['username'])

        dv_user_data = dict(user=reg_opendp_user.object_id,
                            dv_handoff=self.bad_handoff_id)

        resp = self.client.post(self.dv_user_url,
                                data=dv_user_data,
                                format='json')

        # print('resp.status', resp.status_code)
        # print('resp.content', resp.content)

        # Should be a 400 status code
        self.assertEqual(resp.status_code, http_status.HTTP_400_BAD_REQUEST)
