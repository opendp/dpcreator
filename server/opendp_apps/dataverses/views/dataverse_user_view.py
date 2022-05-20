import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from opendp_apps.user.models import OpenDPUser, DataverseUser
from opendp_apps.dataverses.serializers import DataverseUserSerializer
from opendp_apps.user.dataverse_user_initializer import DataverseUserInitializer
from opendp_project.views import BaseModelViewSet


logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DataverseUserView(BaseModelViewSet):

    def get_serializer(self, instance=None):
        return DataverseUserSerializer(context={'request': instance})

    def xget_queryset(self):
        """
        Note: see Issue https://github.com/opendp/dpcreator/issues/530
        Retrieve DataverseUser objects related to the logged in User
          - OpenDPUser (logged in user)
            - DataverseUser (FK to OpenDPUser)
        """
        return DataverseUser.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Used to Create or update a DataverseUser immediately following
        SocialAuth account creation or login where a Handoff ID is present
        """
        user_id = request.data.get('user')
        handoff_id = request.data.get('dv_handoff')

        # (1) Retrieve the OpenDPUser
        #

        try:
            opendp_user = OpenDPUser.objects.get(object_id=user_id)
        except OpenDPUser.DoesNotExist:
            logger.error(f'DataverseUserView: No OpenDPUser found for id: {user_id}')
            return Response({'success': False,
                             'message': f'No OpenDPUser found for id: {user_id}'},
                            status=status.HTTP_400_BAD_REQUEST)

        # (2) Update the DataverseUser object
        #
        util = DataverseUserInitializer.create_update_dv_user_workflow(opendp_user, handoff_id)
        if util.has_error():
            logger.error(f'DataverseUserView: {util.get_err_msg()}')
            return Response({'success': False, 'message': util.get_err_msg()},
                            status=util.http_resp_code)

        logger.info(f'DataverseUserView: DataverseUser created with id {util.dv_user.object_id}')
        return Response({'success': True,
                         'data': {'dv_user': util.dv_user.object_id}},
                        status=util.http_resp_code)

    def update(self, request, *args, **kwargs):
        """Update the Dataverse User. Expects JSON"""
        opendp_user_id = request.data.get('user')
        handoff_id = request.data.get('dv_handoff')

        # (1) Retrieve the OpenDPUser
        #
        try:
            opendp_user = OpenDPUser.objects.get(object_id=opendp_user_id)
        except OpenDPUser.DoesNotExist:
            logger.error(f'DataverseUserView: No OpenDPUser found for id: {opendp_user_id}')
            return Response({'success': False,
                             'message': f'No OpenDPUser found for id: {opendp_user_id}'},
                             status=status.HTTP_400_BAD_REQUEST)

        # (2) Update the DataverseUser object
        #
        util = DataverseUserInitializer.create_update_dv_user_workflow(opendp_user, handoff_id)
        if util.has_error():
            logger.error(f'DataverseUserView: Error updating DataverseUser with opendp_user: {opendp_user.object_id} '
                         f'and handoff_id: {handoff_id}: {util.get_err_msg()}')
            return Response({'success': False, 'message': util.get_err_msg()},
                            status=util.http_resp_code)

        logger.error(f'Successfully updated DataverseUser {util.dv_user.object_id}')
        return Response({'success': True,
                         'data': {'dv_user': util.dv_user.object_id}},
                        status=util.http_resp_code)
