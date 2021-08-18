from rest_framework import serializers

from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses.models import RegisteredDataverse, DataverseHandoff
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.user.models import DataverseUser, OpenDPUser


class RegisteredDataverseSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisteredDataverse
        fields = ['name', 'dataverse_url',
                  'object_id', 'active',
                  'created', 'updated']

class DataverseUserSerializer(serializers.ModelSerializer):

    user = serializers.SlugRelatedField(queryset=OpenDPUser.objects.all(),
                                        slug_field='object_id',
                                        read_only=False)
    dv_handoff = serializers.SlugRelatedField(queryset=DataverseHandoff.objects.all(),
                                              slug_field='object_id',
                                              read_only=False)

    # This will mean that the form at http://localhost:8000/api/dv-user/ will only have those three fields,
    class Meta:
        model = DataverseUser
        fields = ['object_id', 'user', 'dv_handoff']

    def save(self, **kwargs):
        # print(f"(serializer) validated data: {self.validated_data}")
        dataverse_handoff = self.validated_data.pop('dv_handoff')
        self.validated_data['dv_installation'] = dataverse_handoff.dv_installation
        self.validated_data['dv_general_token'] = dataverse_handoff.apiGeneralToken
        return super().save()

    def update(self, instance, validated_data):
        # print(f"instance: {instance}, validated_data: {validated_data}")
        opendp_user = OpenDPUser.objects.get(object_id=validated_data.get('user'))
        instance.email = opendp_user.email
        instance.first_name = opendp_user.first_name
        instance.last_name = opendp_user.last_name
        # instance.dv_general_token = validated_data.get('dv_general_token')
        # instance.dv_sensitive_token = validated_data.get('dv_sensitive_token')
        # instance.dv_token_update = validated_data.get('dv_token_update')
        instance.save()
        return instance


class DataverseHandoffSerializer(serializers.ModelSerializer):

    site_url = serializers.SlugRelatedField(queryset=RegisteredDataverse.objects.all(),
                                            slug_field='dataverse_url',
                                            read_only=False,
                                            source='dv_installation')

    class Meta:
        model = DataverseHandoff
        exclude = ['dv_installation']


class DataverseFileInfoSerializer(serializers.ModelSerializer):

    dv_installation = serializers.PrimaryKeyRelatedField(queryset=RegisteredDataverse.objects.all())
    creator = serializers.PrimaryKeyRelatedField(queryset=OpenDPUser.objects.all())

    class Meta:
        model = DataverseFileInfo
        exclude = ['data_profile', 'source_file', 'polymorphic_ctype']
