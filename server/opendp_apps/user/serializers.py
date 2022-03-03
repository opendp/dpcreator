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
        model = settings.AUTH_USER_MODEL
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
    handoff_id = serializers.UUIDField(required=False)

    def validate_handoff_id(self, value):
        """
        Validate that the handoffId has an existing DataverseHandoff object
        """
        print('CustomRegisterSerializer.validate_handoff_id')
        if not value:
            return value

        try:
            DataverseHandoff.objects.get(object_id=value)
        except DataverseHandoff.DoesNotExist:
            raise serializers.ValidationError("DataverseHandoff does not exist")

        return value

    def authenticate(self, **kwargs):
        """Override authenticate method"""
        print('authenticate kwargs:', kwargs)
        return super().authenticate(**kwargs)

        #return authenticate(self.context['request'], **kwargs)


class CustomRegisterSerializer(RegisterSerializer):
    """
    Add the "handoff_id". As well as creating an OpenDP User, also
    create/update related objects: DataverseUser and DataverseFileInfo
    """
    objectId = serializers.models.UUIDField
    handoff_id = serializers.models.UUIDField

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
        handoff_id = self.data.get('handoff_id')

        # next line for testing until UI is updated
        if handoff_id is None:
            handoff_id = DataverseHandoff.objects.all()[0].object_id

        # !! Future note: If there is no handoff_id, then simply return the user
        #  e.g. It's not a Dataverse case.


        util = DataverseUserInitializer(user, handoff_id)
        if util.has_error():
            print('CustomRegisterSerializer.save 2a')
            print('util.get_err_msg()', util.get_err_msg())
            raise serializers.ValidationError(detail=util.get_err_msg())

        print('CustomRegisterSerializer save 3')
        return user

