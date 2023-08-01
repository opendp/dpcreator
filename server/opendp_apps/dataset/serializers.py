from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from rest_polymorphic.serializers import PolymorphicSerializer

from opendp_apps.analysis.serializers import AnalysisPlanSerializer
from opendp_apps.dataset import static_vals as dstatic
from opendp_apps.dataset.models import DepositorSetupInfo, DatasetInfo, DataverseFileInfo, UploadFileInfo
from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.model_helpers.basic_response import BasicResponse, ok_resp, err_resp
from opendp_apps.user.models import OpenDPUser


class DatasetObjectIdSerializer(serializers.Serializer):
    """Ensure input is a valid UUID and connected to a valid DatasetInfo object"""
    object_id = serializers.UUIDField()

    def validate_object_id(self, value):
        """
        Check that the object_id belongs to an existing DatasetInfo object
        """
        try:
            dsi = DatasetInfo.objects.get(object_id=value)
            self.dataset_info = dsi
        except DatasetInfo.DoesNotExist:
            raise serializers.ValidationError(dstatic.ERR_MSG_DATASET_INFO_NOT_FOUND)

        return value

    def get_dataset_info(self) -> BasicResponse:
        """Get the related DatasetInfo object"""
        assert self.is_valid(), "Do not call this method before checking \".is_valid()\""

        try:
            dsi = DatasetInfo.objects.get(object_id=self.validated_data.get('object_id'))
        except DatasetInfo.DoesNotExist:
            return err_resp(dstatic.ERR_MSG_DATASET_INFO_NOT_FOUND)

        return ok_resp(dsi)

    def get_object_id(self):
        """Return the object_id, this will be a str or None"""
        assert self.is_valid(), "Do not call this method before checking \".is_valid()\""

        return self.validated_data.get('object_id')

    def get_dataset_info_with_user_check(self, user: get_user_model()) -> BasicResponse:
        """Get the related DatasetInfo object and check that the user matches the creator"""
        assert self.is_valid(), "Do not call this method before checking \".is_valid()\""

        try:
            dsi = DatasetInfo.objects.get(object_id=self.validated_data.get('object_id'),
                                          creator=user)
        except DatasetInfo.DoesNotExist:
            return err_resp(dstatic.ERR_MSG_DATASET_INFO_NOT_FOUND_CURRENT_USER)

        return ok_resp(dsi)


class DatasetInfoSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(queryset=OpenDPUser.objects.all(),
                                           slug_field='username',
                                           read_only=False)

    analysis_plans = AnalysisPlanSerializer(many=True, read_only=True, source='analysisplan_set')

    class Meta:
        model = DatasetInfo
        fields = ['object_id',
                  'name',
                  'description',
                  'depositor_setup_info',
                  'creator',
                  'created',
                  'source',
                  'analysis_plans',
                  'status',
                  'status_name']

        read_only_fields = ['object_id',
                            'id',
                            'depositor_setup_info',
                            'created',
                            'creator',
                            'source',
                            'status',
                            'status_name']


class DepositorSetupInfoSerializer(serializers.ModelSerializer):
    """Serializer for the DepositorSetupInfo"""
    creator_name = serializers.CharField(source='creator', read_only=True)
    creator_id = serializers.CharField(source='creator.object_id', read_only=True)

    class Meta:
        model = DepositorSetupInfo
        fields = ['object_id',
                  'creator_id',
                  'creator_name',
                  'is_complete',
                  'user_step',
                  'wizard_step',
                  'dataset_questions',
                  'epsilon_questions',
                  'dataset_size',
                  'data_profile',
                  'variable_info',
                  'default_epsilon', 'epsilon',
                  'default_delta', 'delta',
                  'confidence_level',
                  'created', 'updated',
                  ]
        read_only_fields = ['object_id',
                            'creator_id',
                            'creator_name',
                            'user_step',
                            'data_profile',
                            'default_epsilon',
                            'default_delta',
                            'created',
                            'updated', ]

    def update(self, instance, validated_data):
        """
        (Is this still valid? Why was there a race condition? RP, 5/24/2023)
        Override default update method to counteract race conditions.
        (See https://github.com/encode/django-rest-framework/issues/5897)
        :param instance:
        :param validated_data:
        :return:
        """
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)
        update_fields = []

        for attr, value in validated_data.items():
            update_fields.append(attr)
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)

        # Specifically for this model, we are overriding the update method with an explicit list of
        # update_fields, so we need to set the updated field manually.
        # All other models will be updated without this step due to the auto_now option from the parent class.
        instance.updated = timezone.now()
        instance.save(update_fields=update_fields)

        return instance


class DataverseFileInfoSerializer(DatasetInfoSerializer):
    creator = serializers.SlugRelatedField(queryset=OpenDPUser.objects.all(),
                                           slug_field='username',
                                           read_only=False)

    installation_name = serializers.SlugRelatedField(queryset=RegisteredDataverse.objects.all(),
                                                     slug_field='name',
                                                     read_only=False,
                                                     source='dv_installation')

    depositor_setup_info = DepositorSetupInfoSerializer(read_only=True)

    dataset_schema_info = serializers.JSONField(read_only=True)

    file_schema_info = serializers.JSONField(read_only=True)

    analysis_plans = AnalysisPlanSerializer(many=True,
                                            read_only=True,
                                            source='analysisplan_set')

    class Meta:
        model = DataverseFileInfo
        fields = ['object_id', 'name', 'created', 'creator', 'installation_name',
                  'dataverse_file_id', 'dataset_doi',
                  'file_doi',
                  'status',
                  'status_name',
                  'depositor_setup_info',
                  'dataset_schema_info',
                  'file_schema_info',
                  'depositor_setup_info',
                  'analysis_plans']
        readonly_fields = ['depositor_setup_info',]
        extra_kwargs = {
            'url': {'view_name': 'dataset-info-list'},
        }


class UploadFileInfoSerializer(serializers.ModelSerializer):
    """
    Used when returning UploadFileInfo objects, including upon creation
    """
    creator_id = serializers.CharField(source='creator.object_id', read_only=True)

    creator_name = serializers.CharField(source='creator', read_only=True)

    depositor_setup_info = DepositorSetupInfoSerializer(read_only=True)

    dataset_schema_info = serializers.JSONField(read_only=True)

    file_schema_info = serializers.JSONField(read_only=True)

    analysis_plans = AnalysisPlanSerializer(many=True,
                                            read_only=True,
                                            source='analysisplan_set')

    class Meta:
        model = UploadFileInfo
        fields = ['object_id',
                  'name',
                  'description',
                  'creator_id',
                  'creator_name',
                  'source',
                  'depositor_setup_info',
                  'status', 'status_name',
                  'dataset_schema_info', 'file_schema_info',  # previously used for DataverseFileInfo
                  'analysis_plans',
                  'created',
                  'updated',
                  ]
        read_only_fields = ['id',
                            'object_id',
                            'creator',
                            'source',
                            'source_file',
                            'status',
                            'created',
                            'updated']
        extra_kwargs = {
            'url': {'view_name': 'dataset-info-list'},
        }


class UploadFileInfoCreationSerializer(serializers.ModelSerializer):
    """
    Used only for UploadFileInfo creation.
    Even with creation, returned info is: UploadFileInfoSerializer
    """
    name = serializers.CharField()
    source_file = serializers.FileField(use_url=False)
    creator = serializers.SlugRelatedField(slug_field='object_id',
                                           queryset=OpenDPUser.objects.all())

    class Meta:
        model = UploadFileInfo
        fields = ['object_id', 'name', 'source_file', 'creator', ]

    def save(self, **kwargs):
        return super().save(**kwargs)


class DatasetInfoPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        #DatasetInfo: DatasetInfoSerializer,
        DataverseFileInfo: DataverseFileInfoSerializer,
        UploadFileInfo: UploadFileInfoSerializer
    }
