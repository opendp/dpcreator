from rest_framework import serializers

from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.dp_mean import dp_mean


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
    error = serializers.CharField(allow_blank=True)
    label = serializers.CharField()
    locked = serializers.BooleanField()
    epsilon = serializers.FloatField()
    variable = serializers.CharField()
    statistic = serializers.ChoiceField(choices=['mean', 'sum', 'count', 'histogram', 'quantile'])
    fixed_value = serializers.CharField()
    handle_as_fixed = serializers.BooleanField()
    missing_values_handling = serializers.ChoiceField(choices=['drop', 'insert_random', 'insert_fixed'])


class ReleaseInfoSerializer(serializers.ModelSerializer):
    dp_statistics = serializers.ListField(child=DPStatisticSerializer())

    class Meta:
        model = ReleaseInfo
        fields = ('dp_statistics', )

    def save(self, **kwargs):
        """
        Validate each release request and return any errors that arise.
        A bit of a misuse of the "save" terminology since we aren't creating
        any rows in the database, but consistent with the fact that this is a post.
        Expects a request of the form:
        {
            "analysis_plan_id": 0,
            "dp_statistics": [{
                 "error": "",
                 "label": "EyeHeight",
                 "locked": false,
                 "epsilon": 0.0625,
                 "variable": "eyeHeight",
                 "statistic": "mean",
                 "fixed_value": "5",
                 "handle_as_fixed": true,
                 "missing_values_handling": "insert_fixed"
                 },
                {
                 "error": "",
                 "label": "EyeHeight",
                 "locked": false,
                 "epsilon": 0.0625,
                 "variable": "eyeHeight",
                 "statistic": "count",
                 "fixed_value": "5",
                 "handle_as_fixed": true,
                 "missing_values_handling": "insert_fixed"
                 }
            ]
         }
        :param kwargs:
        :return:
        """
        stats_valid = []
        for dp_stat in self.validated_data['dp_statistics']:
            statistic = dp_stat['statistic']
            # Do some validation and append to stats_valid
            if statistic == 'mean':
                index = 0
                lower = 0.
                upper = 100.
                n = 1000
                impute = dp_stat['missing_values_handling'] != 'drop'
                impute_value = float(dp_stat['fixed_value'])
                epsilon = float(dp_stat['epsilon'])
                try:
                    print(index, lower, upper, n, impute_value, dp_stat['epsilon'])
                    print(list(map(type, (index, lower, upper, n, impute_value, dp_stat['epsilon']))))
                    preprocessor = dp_mean(index, lower, upper, n, impute_value, epsilon)
                    stats_valid.append({'valid': True})
                except Exception as ex:
                    stats_valid.append({
                        'valid': False,
                        'message': str(ex)
                    })
            else:
                # For now, everything else is invalid
                stats_valid.append({
                    'valid': False,
                    'message': f'Statistic \'{statistic}\' is not supported'
                })
        # super(ReleaseInfoSerializer).save(**kwargs)
        return stats_valid

