from json import JSONDecodeError

from django.http import JsonResponse
from requests.exceptions import InvalidSchema
from rest_framework import viewsets, status

from opendp_apps.dataverses.dataverse_client import DataverseClient
from opendp_apps.dataverses.dv_user_handler import DataverseUserHandler, DataverseResponseError
from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.serializers import DataverseUserSerializer
from opendp_apps.utils.view_helper import get_json_error, get_json_success


class DataverseUserView(viewsets.ViewSet):

    def get_serializer(self, instance=None):
        return DataverseUserSerializer(context={'request': instance})

    def create(self, request):
        """Expects JSON. Given object_ids for OpenDPUser and DataverseHandoff objects,
        retrieve the user's information from Dataverse and create a DataverseUser"""

        # ----------------------------------
        # Validate the input
        # ----------------------------------
        # print(f"data: {request.data}")

        dataverse_user_serializer = DataverseUserSerializer(data=request.data, context={'request': request})
        if not dataverse_user_serializer.is_valid():
            print("INVALID SERIALIZER")
            print(request.data)
            return JsonResponse(get_json_error(dataverse_user_serializer.errors),
                                status=status.HTTP_400_BAD_REQUEST)

        #print(f"DataverseUserSerializer.validated_data: {dataverse_user_serializer.validated_data}")
        try:
            dataverse_user = dataverse_user_serializer.save()
        except DataverseHandoff.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No such DataVerse exists'})
        opendp_user = dataverse_user_serializer.validated_data.get('user')


        # ----------------------------------
        # Call the Dataverse API
        # ----------------------------------

        site_url = DataverseHandoff.objects.get(id=request.data['dv_handoff']).siteUrl
        api_general_token = dataverse_user.dv_general_token
        dataverse_client = DataverseClient(site_url, api_general_token)
        try:
            dataverse_response = dataverse_client.get_user_info(user_api_token=api_general_token)
        except InvalidSchema:
            print("INVALID SCHEMA")
            return JsonResponse(get_json_error(f'The Site {site_url} is not valid'),
                                status=400)
        except JSONDecodeError:
            return JsonResponse(get_json_error(f'Error reading data from {site_url}'),
                                status=status.HTTP_400_BAD_REQUEST)

        if dataverse_response.success is not True:
            print("DATAVERSE RESPONSE FAILURE")
            return JsonResponse(get_json_error(dataverse_response.message),
                                status=400)

        # ----------------------------------
        # Create the DataverseUser object
        # ----------------------------------
        try:
            handler = DataverseUserHandler(opendp_user.id, site_url,
                                           api_general_token,
                                           dataverse_response.__dict__)
            new_dv_user = handler.create_dataverse_user()
            new_dv_user.save()
        except DataverseResponseError as ex:
            print("DV RESPONSE ERROR")
            return JsonResponse(get_json_error(f'Error {ex}'),
                                status=400)

        #print(dataverse_response.__dict__)
        return JsonResponse(get_json_success('success',
                                             data={'dv_user': new_dv_user.object_id}),
                            status=201)

    def update(self, request, pk=None):
        """Update the Dataverse User. Expects JSON"""
        # ----------------------------------
        # Validate the input
        # ----------------------------------
        #print(f"data: {request.data}")

        dataverse_user_serializer = DataverseUserSerializer(data=request.data, context={'request': request})
        if not dataverse_user_serializer.is_valid():
            print("INVALID SERIALIZER")
            return JsonResponse(get_json_error(dataverse_user_serializer.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        #print(f"DataverseUserSerializer.validated_data: {dataverse_user_serializer.validated_data}")
        try:
            dataverse_user = dataverse_user_serializer.save()
        except DataverseHandoff.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No such DataVerse exists'})
        opendp_user = dataverse_user_serializer.validated_data.get('user')

        # ----------------------------------
        # Call the Dataverse API
        # ----------------------------------

        site_url = DataverseHandoff.objects.get(id=request.data['dv_handoff']).siteUrl
        api_general_token = dataverse_user.dv_general_token
        dataverse_client = DataverseClient(site_url, api_general_token)
        try:
            #print(f"API token: {api_general_token}")
            #print(f"Dataverse Client: {dataverse_client.__dict__}")
            dataverse_response = dataverse_client.get_user_info(user_api_token=api_general_token)
        except InvalidSchema:
            print("INVALID SCHEMA")
            return JsonResponse(get_json_error(f'The Site {site_url} is not valid'),
                                status=400)
        except JSONDecodeError:
            return JsonResponse(get_json_error(f'Error reading data from {site_url}'),
                                status=status.HTTP_400_BAD_REQUEST)

        if dataverse_response.success is not True:
            print("DATAVERSE RESPONSE FAILURE")
            return JsonResponse(get_json_error(dataverse_response.message),
                                status=400)

        # ----------------------------------
        # Update the DataverseUser object
        # ----------------------------------
        try:
            handler = DataverseUserHandler(opendp_user.id, site_url,
                                           api_general_token,
                                           dataverse_response.__dict__)
            update_resp = handler.update_dataverse_user()
            if update_resp.success:
                updated_dv_user = update_resp.data
                updated_dv_user.save()
            else:
                return JsonResponse(get_json_error(update_resp.message), status=status.HTTP_400_BAD_REQUEST)
        except DataverseResponseError as ex:
            print("DV RESPONSE ERROR")
            return JsonResponse(get_json_error(f'Error {ex}'),
                                status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(get_json_success('updated',
                                             data=dict(dv_user=updated_dv_user.object_id)),
                            status=201)