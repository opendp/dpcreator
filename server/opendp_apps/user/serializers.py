from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from django.contrib.auth.models import Group
from django.db import transaction
from rest_framework import serializers

from opendp_apps.user.dataverse_user_initializer import DataverseUserInitializer
from .models import OpenDPUser
from ..dataverses.models import DataverseHandoff

"""
class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'
"""


class OpenDPUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenDPUser
        fields = ['url', 'username', 'email', 'groups', 'object_id', 'handoff_id']


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
    handoffId = serializers.UUIDField(required=False, allow_null=True)

    def validate_handoffId(self, handoff_id):
        """
        The handoffId may be None or an existing DataverseHandoff object
        """
        if not handoff_id:
            return None

        try:
            _dv_handoff = DataverseHandoff.objects.get(object_id=handoff_id)
        except DataverseHandoff.DoesNotExist:
            raise serializers.ValidationError("DataverseHandoff does not exist")

        return handoff_id

    def authenticate(self, **kwargs):
        """Override authenticate method"""
        user = super().authenticate(**kwargs)

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
        if not handoff_id:
            return None

        try:
            _dv_handoff = DataverseHandoff.objects.get(object_id=handoff_id)
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
        user = super().save(request)
        user.save()

        # If a handoffId is included, then create a related DataverseUser object
        #
        handoff_id = self.data.get('handoffId')
        if handoff_id:
            util = DataverseUserInitializer.create_update_dv_user_workflow(user, handoff_id)
            if util.has_error():
                # Delete the DataverseHandoff object
                DataverseHandoff.delete_handoff(handoff_id)
                # Raise an error
                raise serializers.ValidationError(detail=util.get_err_msg())
            else:
                # The DataverseUser has been successfully created:
                #  - Save a temp reference to the DataverseHandoff for
                #    when the OpenDPUser logs in
                user.handoff_id = handoff_id
                user.save()

        return user
