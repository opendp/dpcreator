import re
import pandas as pd

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.dp_mean import dp_mean


class AnalysisPlanObjectIdSerializer(serializers.Serializer):
    """Ensure input is a valid UUID and connected to a valid DataSetInfo object"""
    object_id = serializers.UUIDField()

    def validate_object_id(self, value):
        """
        Check that the object_id belongs to an existing AnalysisPlan object
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


class AnalysisPlanPKRelatedField(PrimaryKeyRelatedField):

    def __init__(self, **kwargs):
        self.pk_field = 'object_id'
        super(AnalysisPlanPKRelatedField, self).__init__(**kwargs)

    def get_queryset(self):
        return AnalysisPlan.objects.all()

    def to_representation(self, value):
        return value.object_id


class ComputationChainSerializer(serializers.Serializer):
    dp_statistics = serializers.ListField(child=DPStatisticSerializer())
    analysis_plan_id = serializers.UUIDField()

    def run_computation_chain(self):
        analysis_plan = AnalysisPlan.objects.get(object_id=self.validated_data['analysis_plan_id'])
        results = []
        df = pd.read_csv(analysis_plan.dataset.source_file.file, delimiter='\t')

        for dp_stat in self.validated_data['dp_statistics']:
            statistic = dp_stat['statistic']
            label = dp_stat['label']
            variable_info = analysis_plan.variable_info[label]
            index = 'SCM'  # TODO: column headers.... (variable_info['index'])
            column = df[index]
            lower = variable_info.get('min')
            upper = variable_info.get('max')
            if lower is None:
                raise Exception(f"Lower must be defined: {variable_info}")
            if upper is None:
                raise Exception(f"Upper must be defined: {variable_info}")
            # n = analysis_plan.data_set.data_profile.get('dataset', {}).get('row_count', 1000)
            n = 1000
            impute = dp_stat['missing_values_handling'] != 'drop'
            impute_value = float(dp_stat['fixed_value'])
            epsilon = float(dp_stat['epsilon'])
            # Do some validation and append to stats_valid
            if statistic == 'mean':
                try:
                    preprocessor = dp_mean(index, lower, upper, n, impute_value, epsilon)
                    results.append({'column': column, 'statistic': statistic, 'result': preprocessor(column)})
                # TODO: add column index and statistic to result
                except Exception as ex:
                    results.append({
                        'column': column,
                        'statistic': statistic,
                        'valid': False,
                        'message': str(ex)
                    })
                    raise ex
            else:
                # For now, everything else is invalid
                results.append({
                    'column_index': index,
                    'statistic': statistic,
                    'valid': False,
                    'message': f'Statistic \'{statistic}\' is not supported'
                })
        return results



class ReleaseValidationSerializer(serializers.ModelSerializer):
    dp_statistics = serializers.ListField(child=DPStatisticSerializer())
    analysis_plan_id = serializers.UUIDField()

    class Meta:
        model = ReleaseInfo
        fields = ('dp_statistics', 'analysis_plan_id', )

    def _camel_to_snake(self, name):
        """
        Front end is passing camelCase, but JSON in DB is using snake_case
        :param name:
        :return:
        """
        return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    def save(self, **kwargs):
        """
        Validate each release request and return any errors that arise.
        A bit of a misuse of the "save" terminology since we aren't creating
        any rows in the database, but consistent with the fact that this is a post.
        Expects a request of the form:
        {
            "analysis_plan_id": abcd-1234,
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
        analysis_plan = AnalysisPlan.objects.get(object_id=self.validated_data['analysis_plan_id'])
        stats_valid = []
        for dp_stat in self.validated_data['dp_statistics']:
            statistic = dp_stat['statistic']
            label = self._camel_to_snake(dp_stat['label'])
            variable_info = analysis_plan.variable_info[label]
            index = 0  # TODO: column headers.... (variable_info['index'])
            lower = variable_info.get('min')
            upper = variable_info.get('max')
            if lower is None:
                raise Exception(f"Lower must be defined: {variable_info}")
            if upper is None:
                raise Exception(f"Upper must be defined: {variable_info}")
            # n = analysis_plan.data_set.data_profile.get('dataset', {}).get('row_count', 1000)
            n = 1000
            impute = dp_stat['missing_values_handling'] != 'drop'
            impute_value = float(dp_stat['fixed_value'])
            epsilon = float(dp_stat['epsilon'])
            # Do some validation and append to stats_valid
            if statistic == 'mean':
                try:
                    # print(index, lower, upper, n, impute_value, dp_stat['epsilon'])
                    # print(list(map(type, (index, lower, upper, n, impute_value, dp_stat['epsilon']))))
                    preprocessor = dp_mean(index, lower, upper, n, impute_value, epsilon)
                    stats_valid.append({'valid': True})
                # TODO: add column index and statistic to result
                except Exception as ex:
                    stats_valid.append({
                        'column_index': index,
                        'statistic': statistic,
                        'valid': False,
                        'message': str(ex)
                    })
                    raise ex
            else:
                # For now, everything else is invalid
                stats_valid.append({
                    'column_index': index,
                    'statistic': statistic,
                    'valid': False,
                    'message': f'Statistic \'{statistic}\' is not supported'
                })
        # super(ReleaseInfoSerializer).save(**kwargs)
        return stats_valid

