from django.contrib.auth.models import Group
from django.conf import settings

from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.db import transaction
from .models import OpenDPUser, DataverseUser
from ..dataverses.models import DataverseHandoff
from ..utils.view_helper import get_object_or_error_response

from opendp_apps.user.dataverse_user_initializer import DataverseUserInitializer

"""
class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'
"""


class OpenDPUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ['url', 'username', 'email', 'groups', 'object_id']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class CustomRegisterSerializer(RegisterSerializer):
    objectId = serializers.models.UUIDField
    handoffId = serializers.models.UUIDField

    def validate_handoffId(self, value):
        """
        Validate that the handoffId has an existing DataverseHandoff object
        """
        print('CustomRegisterSerializer.validate_handoffId')
        try:
            DataverseHandoff.objects.get(object_id=value)
        except DataverseHandoff.DoesNotExist:
            raise serializers.ValidationError("DataverseHandoff does not exist")

        return value

    # Define transaction.atomic to rollback the save operation in case of error
    @transaction.atomic
    def save(self, request):
        print('CustomRegisterSerializer.save 1')
        """Override the save method"""
        user = super().save(request)

        user.objectId = self.data.get('objectId')
        user.save()

        print('CustomRegisterSerializer.save 2')

        # As part of a longer workflow, create or update the
        #   DataverseUser as well as DataverseFileInfo
        #
        handoff_id = self.data.get('handoffId')
        if handoff_id is None:
            handoff_id = DataverseHandoff.objects.all()[0].object_id
        util = DataverseUserInitializer(user, handoff_id)
        if util.has_error():
            print('CustomRegisterSerializer.save 2a')
            print('util.get_err_msg()', util.get_err_msg())
            raise serializers.ValidationError(detail=util.get_err_msg())

        print('CustomRegisterSerializer save 3')
        return user

