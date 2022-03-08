from rest_framework import status
from rest_framework.response import Response

from opendp_apps.user.models import DataverseUser
from opendp_apps.dataverses.serializers import DataverseUserSerializer
from opendp_apps.user.dataverse_user_initializer import DataverseUserInitializer
from opendp_apps.utils.view_helper import get_json_error, get_json_success, get_object_or_error_response
from opendp_project.views import BaseModelViewSet


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

        resp = DataverseUserInitializer.create_update_dv_user_social_auth(user_id, handoff_id)
        if not resp.success:
            return Response(get_json_error(resp.message), status=status.HTTP_400_BAD_REQUEST)

        dv_user_util = resp.data  # Instance of a DataverseUserInitializer w/o errors

        json_resp = {'success': True,
                     'message': 'Success',
                     'data': {'dv_user': dv_user_util.dv_user.object_id}}

        return Response(json_resp, status=dv_user_util.http_resp_code)


    def update(self, request, *args, **kwargs):
        """Update the Dataverse User. Expects JSON"""
        user_id = request.data.get('user')
        handoff_id = request.data.get('dv_handoff')

        resp = DataverseUserInitializer.create_update_dv_user_social_auth(user_id, handoff_id)
        if not resp.success:
            return Response(get_json_error(resp.message), status=status.HTTP_400_BAD_REQUEST)

        dv_user_util = resp.data  # Instance of a DataverseUserInitializer w/o errors

        json_resp = get_json_success('success',
                                     data={'dv_user': dv_user_util.dv_user.object_id})

        return Response(json_resp, status=dv_user_util.http_resp_code)
