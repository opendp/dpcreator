import json

from django.http import JsonResponse
from rest_framework import authentication, permissions
from rest_framework.views import APIView

from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataset.redis import RedisClient


class DepositorSetup(APIView):

    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        """

        """
        mock_dataverse_request = {
            "dataverse_file_id": 1,
            "doi": "doi://123",
            "installation_name": "harvard",
            "dataverse_token": "token"
        }
        # request_body = json.loads(request.data)
        #depositor_setup_info = DepositorSetupInfo.objects.create(epsilon=request.data['epsilon'])

        # TODO: For now, just use DOI as Redis key
        data_profile_key = mock_dataverse_request['doi']
        #redis_client = RedisClient()
        #redis_client.set(data_profile_key, mock_dataverse_request['dataverse_token'])

        ds_info = DataverseFileInfo.objects.create(name=request.data['name'],
                                                   creator=request.user,
                                                   data_profile_key=data_profile_key,
                                                   #depositor_setup_info=depositor_setup_info,
                                                   dataverse_file_id=mock_dataverse_request['dataverse_file_id'],
                                                   doi=mock_dataverse_request['doi'],
                                                   installation_name=mock_dataverse_request['installation_name'])

        print(ds_info.id)
        return JsonResponse({'id': ds_info.id})
