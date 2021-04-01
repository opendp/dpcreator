from rest_framework import serializers

from opendp_apps.dataset.models import DataSetInfo, DataverseFileInfo


class DataSetInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataSetInfo
        fields = ['name', 'creator', 'source']


class DataverseFileInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataverseFileInfo
        fields = ['creator', 'installation_name', 'dataverse_file_id', 'dataset_doi', 'file_doi']