from rest_framework import serializers

from opendp_apps.dataset.models import DataSetInfo


class DataSetInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataSetInfo
        fields = ['name', 'creator', 'source']
