from django.contrib.auth import get_user_model
from django.test import TestCase

from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.serializers import DataverseUserSerializer
from opendp_apps.user.models import DataverseUser


class TestDataverseUserSerializer(TestCase):
    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                'test_opendp_users_01.json']

    def setUp(self):
        self.user_obj, _created = get_user_model().objects.get_or_create(username='dv_depositor')

    def test_create(self):
        serializer = DataverseUserSerializer(data={
            'object_id': '8d24e213-0da3-46cf-ba5c-9f1df5cec53d',
            'dv_installation': '58fd79dc-8541-4aa1-a7c2-85a5b443efa1',
            'user': self.user_obj.object_id,
            'dv_handoff': "9e7e5506-dd1a-4979-a2c1-ec6e59e4769c",
            'persistent_id': 1,
            'email': 'test@test.com',
            'first_name': 'test',
            'last_name': 'test',
            'dv_general_token': 1234
        })
        self.assertEqual(serializer.is_valid(), True)
        dataverse_user = serializer.save()
        # Ensure token from DataverseHandoff makes it onto the new DataverseUser
        self.assertEquals(dataverse_user.dv_general_token, DataverseHandoff.objects.first().apiGeneralToken)

    def test_update(self):
        dataverse_user = DataverseUser.objects.first()
        original_updated = dataverse_user.updated
        serializer = DataverseUserSerializer()
        updated_instance = serializer.update(dataverse_user, validated_data={'user': dataverse_user.user.object_id})
        self.assertNotEqual(original_updated, updated_instance.updated)
