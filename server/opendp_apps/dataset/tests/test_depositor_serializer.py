from unittest import skip

from django.test import TestCase

from opendp_apps.dataset.models import DepositorSetupInfo
from opendp_apps.dataset.serializers import DepositorSetupInfoSerializer
from opendp_apps.model_helpers.msg_util import msgt


@skip('Reconfiguring for analyst mode')
class TestDepositorSerializer(TestCase):
    fixtures = ['test_dataverses_01.json',
                'test_manifest_params_04.json',
                'test_opendp_users_01.json',
                'test_dataset_data_001.json']

    def test_patch_updated_field(self):
        """
        Update instance of DepositorSetupInfo and ensure updated field is updated
        """
        msgt(self.test_patch_updated_field.__doc__.strip())
        self.assertEqual(DepositorSetupInfo.objects.count(), 3)
        # Get current instance and store "updated" field
        instance = DepositorSetupInfo.objects.first()
        original_updated = instance.updated
        # Use serializer to update another field and make sure "updated" changes
        serializer = DepositorSetupInfoSerializer()
        updated_instance = serializer.update(instance, validated_data={'is_complete': True})
        self.assertNotEqual(original_updated, updated_instance.updated)

    def test_is_complete_field(self):
        """
        Update instance of DepositorSetupInfo and ensure is_complete field is updated
        """
        msgt(self.test_is_complete_field.__doc__.strip())
        # Get current instance and store "is_complete" field
        instance = DepositorSetupInfo.objects.filter(is_complete=False).first()
        original_is_complete = instance.is_complete
        self.assertFalse(original_is_complete)
        # Use serializer to update user_step field and make sure "is_complete" changes
        serializer = DepositorSetupInfoSerializer()
        updated_instance = serializer.update(instance, validated_data={'variable_info': {'test': 'something'},
                                                                       'epsilon': 1.0,
                                                                       'user_step': 'step_600'})
        self.assertTrue(updated_instance.is_complete)
