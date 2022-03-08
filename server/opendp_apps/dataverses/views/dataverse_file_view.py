from rest_framework import viewsets, status
from rest_framework.response import Response

from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses.dataverse_client import DataverseClient
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataverses.serializers import DataverseFileInfoMakerSerializer
from opendp_apps.user.models import DataverseUser
from opendp_apps.user.dataverse_user_initializer import DataverseUserInitializer
from opendp_apps.utils.view_helper import get_object_or_error_response
from opendp_project.views import BaseModelViewSet


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
        user_id = request.data.get('creator')

        resp = DataverseUserInitializer.create_dv_file_info(user_id, handoff_id)
        if not resp.success:
            return Response({'success': False, 'message': resp.message},
                            status=status.HTTP_400_BAD_REQUEST)

        dv_user_util = resp.data  # Instance of a DataverseUserInitializer w/o errors

        serializer = DataverseFileInfoMakerSerializer(dv_user_util.dv_file_info,
                                                      context={'request': request})

        return Response({'success': True, 'data': serializer.data},
                        status=dv_user_util.http_resp_code)
