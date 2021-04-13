from json import JSONDecodeError

from django.http import JsonResponse
from requests.exceptions import InvalidSchema
from rest_framework import viewsets, status
from rest_framework.response import Response

from opendp_apps.dataverses.dataverse_client import DataverseClient
from opendp_apps.dataverses.dv_user_handler import DataverseUserHandler, DataverseResponseError
from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.serializers import DataverseUserSerializer
from opendp_apps.user.models import DataverseUser, OpenDPUser
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
        user_id = request.data.get('user')
        handoff_id = request.data.get('dv_handoff')
        try:
            handoff = DataverseHandoff.objects.get(object_id=request.data.get('dv_handoff'))
        except DataverseHandoff.DoesNotExist:
            return Response({'success': False, 'message': 'No Handoff found'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            request.data['user'] = OpenDPUser.objects.get(object_id=user_id)
        except OpenDPUser.DoesNotExist:
            return Response({'success': False,
                             'message': f'OpenDPUser not found with object_id {user_id}'},
                            status=status.HTTP_400_BAD_REQUEST)

        request.data['handoff'] = handoff_id
        request.data['user'] = user_id
        try:
            dataverse_user = DataverseUser.objects.get(user__object_id=user_id, dv_installation=handoff.dv_installation)
            opendp_user = dataverse_user.user
        except DataverseUser.DoesNotExist:
            # ----------------------------------
            # Create the DataverseUser object
            # ----------------------------------
            dataverse_user_serializer = DataverseUserSerializer(data=request.data, context={'request': request})
            if not dataverse_user_serializer.is_valid():
                # print("INVALID SERIALIZER")
                return Response(dataverse_user_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                dataverse_user = dataverse_user_serializer.save()
            except DataverseHandoff.DoesNotExist:
                return Response(dataverse_user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except DataverseUser.DoesNotExist:
                return Response(dataverse_user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            opendp_user = dataverse_user_serializer.validated_data.get('user')

        # ----------------------------------
        # Call the Dataverse API
        # ----------------------------------
        site_url = handoff.siteUrl
        api_general_token = dataverse_user.dv_general_token
        dataverse_client = DataverseClient(site_url, api_general_token)
        try:
            dataverse_response = dataverse_client.get_user_info(user_api_token=api_general_token)
        except InvalidSchema:
            # print("INVALID SCHEMA")
            return Response(get_json_error(f'The Site {site_url} is not valid'), status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return Response(get_json_error(f'Error reading data from {site_url}'), status=status.HTTP_400_BAD_REQUEST)

        if dataverse_response.success is not True:
            # print("DATAVERSE RESPONSE FAILURE")
            return Response(get_json_error(dataverse_response.message), status=status.HTTP_400_BAD_REQUEST)

        try:
            # print(f"OpenDP User id: {opendp_user.id}")
            handler = DataverseUserHandler(opendp_user.id, site_url,
                                           api_general_token,
                                           dataverse_response.__dict__)
            update_response = handler.update_dataverse_user()
            # print(update_response)
        except DataverseResponseError as ex:
            # print("DV RESPONSE ERROR")
            return Response(get_json_error(f'Error {ex}'), status=status.HTTP_400_BAD_REQUEST)

        return Response(get_json_success('success', data={'dv_user': dataverse_user.object_id}),
                        status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        """Update the Dataverse User. Expects JSON"""
        # ----------------------------------
        # Validate the input
        # ----------------------------------
        # print(f"dataverse_user_view: {request.data}")
        try:
            dataverse_user = DataverseUser.objects.get(object_id=pk)
        except DataverseUser.DoesNotExist:
            return Response({'success': False, 'message': 'No Dataverse user found'},
                            status=status.HTTP_400_BAD_REQUEST)
        opendp_user = dataverse_user.user
        request.data['user'] = opendp_user.object_id
        dataverse_user_serializer = DataverseUserSerializer(data=request.data, context={'request': request})
        if dataverse_user_serializer.is_valid():
            try:
                dataverse_user = dataverse_user_serializer.update(dataverse_user, request.data)
            except DataverseHandoff.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'No such DataVerse exists'},
                                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(dataverse_user_serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        opendp_user = dataverse_user_serializer.validated_data.get('user')
        if not opendp_user:
            return Response({'success': False, 'message': 'No OpenDP user found'})

        # ----------------------------------
        # Call the Dataverse API
        # ----------------------------------
        site_url = DataverseHandoff.objects.get(object_id=request.data['dv_handoff']).siteUrl
        api_general_token = dataverse_user.dv_general_token
        dataverse_client = DataverseClient(site_url, api_general_token)
        try:
            dataverse_response = dataverse_client.get_user_info(user_api_token=api_general_token)
        except InvalidSchema:
            # print("INVALID SCHEMA")
            return JsonResponse(get_json_error(f'The Site {site_url} is not valid'),
                                status=400)
        except JSONDecodeError:
            return JsonResponse(get_json_error(f'Error reading data from {site_url}'),
                                status=status.HTTP_400_BAD_REQUEST)

        if dataverse_response.success is not True:
            # print("DATAVERSE RESPONSE FAILURE")
            return JsonResponse(get_json_error(dataverse_response.message),
                                status=400)

        # ----------------------------------
        # Update the DataverseUser object
        # ----------------------------------
        try:
            # print(f"OpenDP user id: {opendp_user.id}")
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
            # print("DV RESPONSE ERROR")
            return JsonResponse(get_json_error(f'Error {ex}'),
                                status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse(get_json_success('updated',
                                             data=dict(dv_user=updated_dv_user.object_id)),
                            status=201)
