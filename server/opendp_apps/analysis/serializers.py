from rest_framework import serializers

from opendp_apps.analysis.models import AnalaysisPlan


class AnalaysisPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalaysisPlan
        fields = ['name', 'object_id',
                  'dataset__object_id',
                  'is_complete', 'user_step',
                  'variable_info', 'dp_statistics',
                  'created', 'updated']

