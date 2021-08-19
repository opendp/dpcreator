from rest_framework import serializers

from opendp_apps.analysis.models import AnalysisPlan


class AnalysisPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisPlan
        fields = ['name', 'object_id',
                  #'dataset',
                  'is_complete', 'user_step',
                  'variable_info', 'dp_statistics',
                  'created', 'updated']

