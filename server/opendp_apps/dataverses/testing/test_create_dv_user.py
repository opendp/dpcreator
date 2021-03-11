from django.test import TestCase
from django.http.response import Http404

from opendp_apps.dataverses.helpers import create_dataverse_user, DataverseResponseError
from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.user.models import OpenDPUser


class CreateDataverseUserTest(TestCase):

    def setUp(self):
        self.opendp_user = OpenDPUser.objects.create(
            username='test',
            email='test@test.test'
        )
        self.registered_dataverse = RegisteredDataverse.objects.create(
            name='test',
            dataverse_url='dataverse.test.com',
            active=True,
            notes='This is a note!'
        )
        self.dataverse_response = {
            'success': True,
            'message': None,
            'data': {
                'status': 'OK',
                'data': {
                    'id': 1234,
                    'identifier': '@username',
                    'displayName': 'Bob Smith',
                    'firstName': 'Bob',
                    'lastName': 'Smith',
                    'email': 'bsmith@email.edu',
                    'superuser': False,
                    'persistentUserId': '823743986739586739586',
                    'emailLastConfirmed': '2020-10-13T22:44:18Z',
                    'createdTime': '2020-10-07T18:31:24Z',
                    'lastLoginTime': '2020-10-07T18:31:24Z',
                    'lastApiUseTime': '2020-10-13T23:10:33Z',
                    'authenticationProviderId': 'google'}
            }
        }
        self.site_url = 'dataverse.test.com'
        self.api_general_token = ''

    def test_create_dataverse_user(self):
        new_dataverse_user = create_dataverse_user(self.opendp_user.id, self.site_url,
                                                   self.api_general_token, self.dataverse_response)
        self.assertEqual(new_dataverse_user.dv_installation_id, 1)
        self.assertEqual(new_dataverse_user.first_name, 'Bob')
        self.assertEqual(new_dataverse_user.last_name, 'Smith')
        self.assertEqual(new_dataverse_user.persistent_id, '823743986739586739586')
        new_dataverse_user.save()
        self.assertEqual(new_dataverse_user.id, 1)

    def test_invalid_dataverse_data_response(self):
        with self.assertRaises(DataverseResponseError):
            dv_response_without_data = self.dataverse_response.copy()
            del dv_response_without_data['data']['data']
            new_dataverse_user = create_dataverse_user(self.opendp_user.id, self.site_url,
                                                       self.api_general_token, dv_response_without_data)

    def test_opendp_user_not_found(self):
        with self.assertRaises(Http404):
            invalid_opendp_user_id = -1
            new_dataverse_user = create_dataverse_user(invalid_opendp_user_id, self.site_url,
                                                       self.api_general_token, self.dataverse_response)

    def test_registered_dataverse_not_found(self):
        with self.assertRaises(Http404):
            invalid_site_url = 'www.thisbreaks.com'
            new_dataverse_user = create_dataverse_user(self.opendp_user.id, invalid_site_url,
                                                       self.api_general_token, self.dataverse_response)
