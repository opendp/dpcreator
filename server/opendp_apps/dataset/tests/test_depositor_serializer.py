from django.test import TestCase

from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataset.serializers import DepositorSetupInfoSerializer
from opendp_apps.model_helpers.msg_util import msgt


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
