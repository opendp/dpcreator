from django.test import TestCase
from django.contrib.auth import get_user_model

from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.serializers import DataverseUserSerializer


class TestDataverseUserSerializer(TestCase):

    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                # This file needs a real token in order to run tests
                'test_dataverse_handoff_01.json',
                'test_opendp_users_01.json',
                'test_dataverse_user_01.json']

    def setUp(self):
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

    def test_create(self):
        serializer = DataverseUserSerializer(data={
            'dv_installation': 1,
            'user': self.user_obj.id,
            'dv_handoff': 1,
            'persistent_id': 1,
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test',
            'dv_general_token': 1234,
            'dv_sensitive_token': 1234,
            'dv_token_update': None
        })
        self.assertEqual(serializer.is_valid(), True)
        dataverse_user = serializer.save()
        # Ensure token from DataverseHandoff makes it onto the new DataverseUser
        self.assertEquals(dataverse_user.dv_general_token, DataverseHandoff.objects.first().apiGeneralToken)
