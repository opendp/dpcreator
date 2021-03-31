from rest_framework import serializers

from opendp_apps.dataverses.models import RegisteredDataverse, DataverseHandoff
from opendp_apps.user.models import DataverseUser, OpenDPUser


class RegisteredDataverseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RegisteredDataverse
        fields = '__all__'


class OpenDPUserSerializer(serializers.ReadOnlyField):
    def to_representation(self, value):
        return {'pk': value.object_id, 'object_id': value.object_id}


class DataverseUserSerializer(serializers.HyperlinkedModelSerializer):

    dv_installation = serializers.PrimaryKeyRelatedField(queryset=RegisteredDataverse.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=OpenDPUser.objects.all())
    dv_handoff = serializers.PrimaryKeyRelatedField(queryset=DataverseHandoff.objects.all())

    # This will mean that the form at http://localhost:8000/api/dv-user/ will only have those three fields,
    class Meta:
        model = DataverseUser
        fields = ['dv_installation', 'user', 'dv_handoff']

    def save(self, **kwargs):
        #print(f"(serializer) validated data: {self.validated_data}")
        dataverse_handoff = self.validated_data.pop('dv_handoff')
        self.validated_data['dv_general_token'] = dataverse_handoff.apiGeneralToken
        self.validated_data['dv_sensitive_token'] = dataverse_handoff.apiSensitiveDataReadToken
        return super().save()


class DataverseHandoffSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataverseHandoff
        exclude = ['apiGeneralToken', 'apiSensitiveDataReadToken']