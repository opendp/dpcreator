import re
import pandas as pd

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField
from django.contrib.auth import get_user_model

from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.dp_mean import dp_mean
from opendp_apps.analysis.validate_release_util import ValidateReleaseUtil
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp

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
    """
    Serializer used for each statistic sent via the API as JSON
    Note: Note "complete" validation" isn't done here -- is instead done in the
    ReleaseValidationSerializer in order to have the possibility of multiple/specific error messages.
    """
    error = serializers.CharField(allow_blank=True)
    label = serializers.CharField()
    locked = serializers.BooleanField()
    epsilon = serializers.FloatField()
    variable = serializers.CharField()

    # e.g. ['mean', 'sum', 'count', 'histogram', 'quantile'] etc.
    statistic = serializers.ChoiceField(choices=astatic.DP_STATS_CHOICES)

    fixed_value = serializers.CharField()
    handle_as_fixed = serializers.BooleanField()

    # e.g. ['drop', 'insert_random', 'insert_fixed']
    missing_values_handling = serializers.ChoiceField(choices=astatic.MISSING_VAL_HANDLING_TYPES)


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
    """
    The purpose of this serializer is to validate individual statistic specifications--with
    each specification described by the DPStatisticSerializer
    """
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
        opendp_user = kwargs.get('opendp_user')
        if not isinstance(opendp_user, get_user_model()):
            user_msg = 'Not an OpenDP User'
            return err_resp(user_msg)

        analysis_plan_id = self.validated_data['analysis_plan_id']

        dp_statistics = self.validated_data['dp_statistics']
        # import json; print('dp_statistics', json.dumps(dp_statistics, indent=4))

        #opendp_user = request.user  # is the user in "save(...)" ?


        validate_util = ValidateReleaseUtil(opendp_user, analysis_plan_id, dp_statistics)
        if validate_util.has_error():
            # This is a big error, check for it before evaluating individual statistics
            #
            user_msg = validate_util.get_err_msg()
            # Can you return a 400 / raise an Exception here with the error message?
            # How should this be used?
            return err_resp(user_msg)   #dict(success=False, message=user_msg)

        print('(validate_util.validation_info)', validate_util.validation_info)
        return ok_resp(validate_util.validation_info)
        #return validate_util.validation_info



"""
Releasing Mean for the variable age. With at least probability 0.95 the output mean will differ from the true mean by at most 0.8328 units. Here the units are the same units the variable has in the dataset.
"""