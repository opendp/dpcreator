from rest_framework import serializers

from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis import static_vals as astatic


class AnalysisPlanObjectIdSerializer(serializers.Serializer):
    """Ensure input is a valid UUID and connected to a valid DataSetInfo object"""
    object_id = serializers.UUIDField()

    def validate_object_id(self, value):
        """
        Check that the object_id belongs to an existing DataSetInfo object
        """
        try:
            plan = AnalysisPlan.objects.get(object_id=value)
        except AnalysisPlan.DoesNotExist:
            raise serializers.ValidationError(astatic.ERR_MSG_NO_ANALYSIS_PLAN)

        return value


    def get_object_id(self):
        """Return the object_id, this will be a str or None"""
        assert self.is_valid(), "Do not call this method before checking \".is_valid()\""

        return self.validated_data.get('object_id')


class AnalysisPlanSerializer(serializers.ModelSerializer):
    analyst = serializers.SlugRelatedField(slug_field='object_id', read_only=True)
    dataset = serializers.SlugRelatedField(slug_field='object_id', read_only=True)

    class Meta:
        model = AnalysisPlan
        fields = ['name', 'object_id',
                  'analyst', 'dataset',
                  'is_complete', 'user_step',
                  'variable_info', 'dp_statistics',
                  'created', 'updated']


class DPStatisticSerializer(serializers.Serializer):
    statistic_type = serializers.ChoiceField(choices=['mean', 'sum', 'count', 'histogram', 'quantile'])
    epsilon = serializers.FloatField()
    missing_values = serializers.ChoiceField(choices=['drop', 'insert_random', 'insert_fixed'])


class ReleaseInfoSerializer(serializers.ModelSerializer):
    dp_statistics = serializers.ListField(child=DPStatisticSerializer())

    class Meta:
        model = ReleaseInfo

    def save(self, **kwargs):
        stats_valid = []
        for dp_stat in self.dp_statistics:
            # Do some validation and append to stats_valid
            pass
        super(ReleaseInfoSerializer).save(**kwargs)
        return stats_valid

