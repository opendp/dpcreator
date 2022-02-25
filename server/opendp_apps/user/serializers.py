from django.contrib.auth.models import Group
from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.db import transaction
from .models import OpenDPUser, DataverseUser
from ..dataverses.models import DataverseHandoff
from ..utils.view_helper import get_object_or_error_response

"""
class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'
"""


class OpenDPUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenDPUser
        fields = ['url', 'username', 'email', 'groups', 'object_id']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class CustomRegisterSerializer(RegisterSerializer):
    objectId = serializers.models.UUIDField
    handoffId = serializers.models.UUIDField

    # Define transaction.atomic to rollback the save operation in case of error

    @transaction.atomic
    def save(self, request):
        user = super().save(request)
        user.objectId = self.data.get('objectId')
        user.save()
        handoff_obj = get_object_or_error_response(DataverseHandoff, object_id=self.data.get('handoffId'))
        dataverse_user = DataverseUser(user=user, dv_installation=handoff_obj.dv_installation)
        dataverse_user.save()
        return user
