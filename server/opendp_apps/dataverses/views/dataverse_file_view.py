import logging

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses.serializers import DataverseFileInfoMakerSerializer
from opendp_apps.user.models import OpenDPUser
from opendp_apps.user.dataverse_user_initializer import DataverseUserInitializer
from opendp_project.views import BaseModelViewSet


logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DataverseFileView(BaseModelViewSet):

    def get_serializer(self, instance=None):
        return DataverseFileInfoMakerSerializer(context={'request': instance})

    def list(self, request, *args, **kwargs):
        # TODO: This is to prevent errors in testing, why is test sending "AnonymousUser" in request?
        if not request.user.id:
            queryset = DataverseFileInfo.objects.all()
        else:
            queryset = DataverseFileInfo.objects.filter(creator=request.user)
        serializer = DataverseFileInfoMakerSerializer(queryset, many=True)
        return Response(data={'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """
        Get a Dataverse File corresponding to a user_id (UUID)
        and values from a DataverseHandoff object
        """
        # TODO: changing user_id to creator to match DB, we should standardize this naming convention
        handoff_id = request.data.get('handoff_id')
        opendp_user_id = request.data.get('creator')

        # (1) Retrieve the OpenDPUser
        #
        try:
            opendp_user = OpenDPUser.objects.get(object_id=opendp_user_id)
        except OpenDPUser.DoesNotExist:
            logger.error(f'DataverseFileView: No OpenDPUser found for id: {opendp_user_id}')
            return Response({'success': False,
                             'message': f'No OpenDPUser found for id: {opendp_user_id}'},
                             status=status.HTTP_400_BAD_REQUEST)

        # (2) Create the DataverseFileInfo object
        #
        util = DataverseUserInitializer.create_dv_file_info(opendp_user, handoff_id)
        if util.has_error():
            logger.error(f'DataverseFileView: {util.get_err_msg()}')
            return Response({'success': False, 'message': util.get_err_msg()},
                            status=util.http_resp_code)

        serializer = DataverseFileInfoMakerSerializer(util.dv_file_info,
                                                      context={'request': request})

        logger.error(f'DataverseFileView: DataverseFileInfo created with request: {request}')
        return Response({'success': True, 'data': serializer.data},
                        status=util.http_resp_code)
