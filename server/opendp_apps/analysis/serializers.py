from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis.validate_release_util import ValidateReleaseUtil
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp
from opendp_apps.utils.extra_validators import validate_min_max


class ReleaseInfoFileDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReleaseInfo
        fields = ('object_id',)


class ReleaseInfoSerializer(serializers.ModelSerializer):
    # Add custom fields to allow download of files directly from DP Creator
    download_json_url = serializers.SerializerMethodField('get_download_json_url')
    download_pdf_url = serializers.SerializerMethodField('get_download_pdf_url')

    def get_download_json_url(self, obj):
        if not obj.dp_release_json_file:
            return None

        download_url = self.context['request'].build_absolute_uri(obj.download_json_url())
        if settings.DPCREATOR_USING_HTTPS:
            download_url = download_url.replace('http://', 'https://')
        return download_url

    def get_download_pdf_url(self, obj):
        if not obj.dp_release_pdf_file:
            return None

        download_url = self.context['request'].build_absolute_uri(obj.download_pdf_url())
        if settings.DPCREATOR_USING_HTTPS:
            download_url = download_url.replace('http://', 'https://')
        return download_url

    class Meta:
        model = ReleaseInfo
        exclude = ('id', 'dataset', 'dp_release_json_file', 'dp_release_pdf_file')


class AnalysisPlanObjectIdSerializer(serializers.Serializer):
    """Ensure input is a valid UUID and connected to a valid DataSetInfo object"""
    object_id = serializers.UUIDField()

    def validate_object_id(self, value):
        """
        Check that the object_id belongs to an existing AnalysisPlan object
        """
        try:
            _plan = AnalysisPlan.objects.get(object_id=value)
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
    release_info = ReleaseInfoSerializer(read_only=True)

    class Meta:
        model = AnalysisPlan
        fields = ['name', 'object_id',
                  'analyst', 'dataset',
                  'is_complete', 'user_step',
                  'variable_info', 'dp_statistics',
                  'release_info',
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
    delta = serializers.FloatField(required=False, default=0.0)
    cl = serializers.FloatField(default=astatic.CL_95)
    variable = serializers.CharField()

    # e.g. ['mean', 'sum', 'count', 'histogram', 'quantile'] etc.
    statistic = serializers.ChoiceField(choices=astatic.DP_STATS_CHOICES)

    fixed_value = serializers.CharField(allow_blank=True)

    # Optional field for boolean stats
    # true_value = serializers.CharField(required=False)
    # false_value = serializers.CharField(required=False)

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


class ReleaseValidationSerializer(serializers.ModelSerializer):
    """
    The purpose of this serializer is to validate individual statistic specifications--with
    each specification described by the DPStatisticSerializer
    """
    dp_statistics = serializers.ListField(child=DPStatisticSerializer())
    analysis_plan_id = serializers.UUIDField()

    class Meta:
        model = ReleaseInfo
        fields = ('dp_statistics', 'analysis_plan_id',)
        # read_only_fields = ('dp_release', )

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

        validate_util = ValidateReleaseUtil.validate_mode(opendp_user, analysis_plan_id, dp_statistics)

        if validate_util.has_error():
            # This is a big error, check for it before evaluating individual statistics
            user_msg = validate_util.get_err_msg()
            # Can you return a 400 / raise an Exception here with the error message?
            # How should this be used?
            return err_resp(user_msg)

        return ok_resp(validate_util.validation_info)


class IntegerEdgeInputsSerializer(serializers.Serializer):
    """Ensure input is a valid UUID and connected to a valid DataSetInfo object"""
    min = serializers.IntegerField()
    max = serializers.IntegerField()
    number_of_bins = serializers.IntegerField(min_value=2)

    def validate(self, data):
        """
        Validation of start and end date.
        """
        try:
            validate_min_max(data['min'], data['max'])
        except ValidationError as err_obj:
            user_msg = f'{err_obj.message}'
            raise serializers.ValidationError(user_msg)

        return data
