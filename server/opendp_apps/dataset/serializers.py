from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataset.models import DataSetInfo, DataverseFileInfo, UploadFileInfo
from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.user.models import OpenDPUser


class DataSetInfoSerializer(serializers.ModelSerializer):

    creator = serializers.SlugRelatedField(queryset=OpenDPUser.objects.all(),
                                           slug_field='username',
                                           read_only=False)

    class Meta:
        model = DataSetInfo
        fields = ['object_id', 'name', 'created', 'creator', 'source', 'status', 'status_name']


class DepositorSetupSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositorSetupInfo
        fields = '__all__'


class DataverseFileInfoSerializer(DataSetInfoSerializer):
    creator = serializers.SlugRelatedField(queryset=OpenDPUser.objects.all(),
                                           slug_field='username',
                                           read_only=False)

    installation_name = serializers.SlugRelatedField(queryset=RegisteredDataverse.objects.all(),
                                                     slug_field='name',
                                                     read_only=False,
                                                     source='dv_installation')

    depositor_setup_info = DepositorSetupSerializer(read_only=True)

    class Meta:
        model = DataverseFileInfo
        fields = ['object_id', 'name', 'created', 'creator', 'installation_name', 'dataverse_file_id', 'dataset_doi',
                  'file_doi', 'status', 'status_name', 'depositor_setup_info']
        extra_kwargs = {
            'url': {'view_name': 'dataset-info-list'},
        }


class UploadFileInfoSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(queryset=OpenDPUser.objects.all(),
                                           slug_field='username',
                                           read_only=False)

    class Meta:
        model = UploadFileInfo
        fields = ['object_id', 'name', 'created', 'creator', 'data_file', 'status', 'status_name']
        extra_kwargs = {
            'url': {'view_name': 'dataset-info-list'},
        }


class DataSetInfoPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        DataSetInfo: DataSetInfoSerializer,
        DataverseFileInfo: DataverseFileInfoSerializer,
        UploadFileInfo: UploadFileInfoSerializer
    }
