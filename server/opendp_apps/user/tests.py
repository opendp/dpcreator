from django.contrib.auth import get_user_model

from django.test import TestCase

from opendp_apps.user.models import OpenDPUser
from opendp_apps.user.serializers import OpenDPUserSerializer


class TestUserSerializer(TestCase):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                # This file needs a real token in order to run tests
                'test_dataverse_handoff_01.json',
                'test_opendp_users_01.json',
                'test_dataverse_user_01.json']

    def setUp(self):
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

    def test_create(self):
        data = {
            'dv_installation': 1,
            'user': 1,
            'dv_handoff': 1,
            'persistent_id': 1,
            'username': 'test_1',
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test',
            'dv_general_token': '1234',
            'dv_sensitive_token': '1234',
            'dv_token_update': '1234'
        }
        user = OpenDPUserSerializer(data=data)
        is_valid = user.is_valid()
        self.assertEqual(is_valid, True)
        self.assertEqual(user.errors, {})
        user.save()
        for k, v in user.validated_data.items():
            self.assertEquals(data.get(k), v)

        self.assertIsNotNone(OpenDPUser.objects.first())
