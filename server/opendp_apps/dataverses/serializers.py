from rest_framework import serializers

from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.user.models import DataverseUser


class RegisteredDataverseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RegisteredDataverse
        fields = '__all__'


class DataverseUserSerializer(serializers.HyperlinkedModelSerializer):

    dv_installation = serializers.ChoiceField(choices=RegisteredDataverse.objects.all())

    class Meta:
        model = DataverseUser
        fields = '__all__'
        # fields = ['user', 'dv_installation', 'persistent_id', 'first_name', 'last_name']
