from django.contrib.auth.models import Group
from django.conf import settings

from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
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
        model = OpenDPUser
        fields = ['url', 'username', 'email', 'groups', 'object_id']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class CustomLoginSerializer(LoginSerializer):
    """
    Add an optional "handoff_id". If the handoff id is included, then use the
    DataverseUserInitializer to create/update related objects: DataverseUser and DataverseFileInfo

    Orig LoginSerializer: https://github.com/iMerica/dj-rest-auth/blob/master/dj_rest_auth/serializers.py
    """
    handoffId = serializers.UUIDField(required=False)

    def validate_handoffId(self, handoff_id):
        """
        The handoffId may be None or an existing DataverseHandoff object
        """
        print('CustomLoginSerializer.validate_handoffId:', handoff_id)
        if not handoff_id:
            return None

        try:
            DataverseHandoff.objects.get(object_id=handoff_id)
        except DataverseHandoff.DoesNotExist:
            raise serializers.ValidationError("DataverseHandoff does not exist")

        return handoff_id

    def authenticate(self, **kwargs):
        """Override authenticate method"""
        print('CustomLoginSerializer.authenticate self.initial_data:', self.initial_data)
        user = super().authenticate(**kwargs)
        print('response', user, type(user))

        # If there's a handoffId, attempt to create/update the DataverseUser
        #
        handoff_id = self.initial_data.get('handoffId')
        print('CustomLoginSerializer.authenticate handoff_id', handoff_id)
        if handoff_id:
            util = DataverseUserInitializer.create_update_dv_user_workflow(user, handoff_id)
            if util.has_error():
                print('CustomLoginSerializer.authenticate; util.get_err_msg', util.get_err_msg())
                pass

        return user

class CustomRegisterSerializer(RegisterSerializer):
    """
    Create an OpenDP User (which happens w/o customization)
    Add the "handoffId". If a "handoffId" is included, also create a DataverseUser

    Orig RegisterSerializer: https://github.com/iMerica/dj-rest-auth/blob/master/dj_rest_auth/registration/serializers.py#L194
    """
    handoffId = serializers.UUIDField(required=False, allow_null=True)

    def validate_handoffId(self, handoff_id):
        """
        The handoffId may be None or an existing DataverseHandoff object
        """
        print('CustomRegisterSerializer.validate_handoffId', handoff_id)
        if not handoff_id:
            return None

        try:
            DataverseHandoff.objects.get(object_id=handoff_id)
        except DataverseHandoff.DoesNotExist:
            raise serializers.ValidationError("DataverseHandoff does not exist")

        return handoff_id

    # Define transaction.atomic to rollback the save operation in case of error
    @transaction.atomic
    def save(self, request):
        """
        Override the save method.
        If a handoffId is included, then create/update a related DataverseUser object
        """
        print('CustomRegisterSerializer.save self.data', self.data)

        user = super().save(request)
        user.save()

        # If a handoffId is included, then create a related DataverseUser object
        #
        handoff_id = self.data.get('handoffId')
        if handoff_id:
            util = DataverseUserInitializer.create_update_dv_user_workflow(user, handoff_id)
            if util.has_error():
                raise serializers.ValidationError(detail=util.get_err_msg())

        return user

