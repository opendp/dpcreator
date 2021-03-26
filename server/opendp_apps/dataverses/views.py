import json
import uuid

from http import HTTPStatus
from requests.exceptions import InvalidSchema

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import get_object_or_404
from rest_framework.parsers import JSONParser
from rest_framework import status

from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse

from opendp_apps.dataverses.serializers import DataverseUserSerializer
from opendp_apps.user.models import DataverseUser, OpenDPUser
from opendp_apps.dataverses.dataverse_client import DataverseClient
from opendp_apps.dataverses.dv_user_handler import DataverseUserHandler, DataverseResponseError
from opendp_apps.utils.view_helper import get_json_error, get_json_success
from opendp_apps.dataverses.models import DataverseHandoff, ManifestTestParams
from opendp_apps.dataverses.forms import DataverseHandoffForm, DataverseUserHandlerForm
from opendp_apps.dataverses import static_vals as dv_static


@login_required
def view_dataverse_handoff(request):
    """Temporarily save the Dataverse paramemeters +
    redirect to the Vue page"""
    if request.method == 'GET':
        # create a form instance and populate it with data from the request:
        form = DataverseHandoffForm(request.GET)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            new_obj = form.save()
            # would redirect to Vue page here!!!

            client_url = reverse('vue-home') + f'?id={str(new_obj.object_id)}'
            print('client_url', client_url)
            return HttpResponseRedirect(client_url)

            # return JsonResponse(dict(message='ok',
            #                          uuid=str(new_obj.object_id)))

        # if a GET (or any other method) we'll create a blank form
        else:
            return JsonResponse(dict(message='Form errors!',
                                data=form.errors))#.as_json()))

    return JsonResponse(dict(message='No GET data!!!!'))


# make superuser only
@login_required
def view_handoff_params_test(request, object_id=None):
    """
    Create a Dataverse user via a POST request
    - OpenDPUser id
    - DataverseHandoff object id
    """
    if not settings.DEBUG:
        raise Http404('Only for testing')

    # ---------------------------------------
    # Change the object_id to a proper UUID
    # ---------------------------------------
    object_as_uuid = None
    try:
        object_as_uuid = uuid.UUID(object_id)
    except ValueError as err_obj:
        message = 'Bad UUID!'
        return JsonResponse(dict(message=message),
                            status=HTTPStatus.BAD_REQUEST)

    # ---------------------------------------
    # Retrieve the DataverseHandoff object
    # ---------------------------------------
    try:
        handoff_params = DataverseHandoff.objects.get(object_id=object_as_uuid)
        message = f'Found params!! {handoff_params}'
    except DataverseHandoff.DoesNotExist:
        message = 'No handoff params found!!'

    info = dict(message=message,
                object_id=object_id)

    return JsonResponse(info)


"""
http://127.0.0.1:8000/api/dataverses/handoff?fileId=4034504&siteUrl=https%3A%2F%2Fdataverse.harvard.edu%2F&apiSensitiveDataReadToken=some-token&apiGeneralToken=some-other-token&datasetPid=doi%3A10.7910%2FDVN%2FB7DHBK&filePid=doi%3A10.7910%2FDVN%2FB7DHBK%2FBSNYLQ

http://127.0.0.1:8000/api/dataverses/view-handoff-params
"""


# Limit this to superusers!!!
@user_passes_test(lambda u: u.is_superuser)
def view_as_dict(request, object_id):
    """Return the ManifestTestParams in JSON format"""
    mparams = ManifestTestParams.objects.filter(object_id=object_id).first()
    if not mparams:
        return JsonResponse(get_json_error('Object not found'), status=HTTPStatus.NOT_FOUND)

    return JsonResponse(get_json_success('Success', data=mparams.as_dict()))


class DataverseUserView(APIView):

    def get_serializer(self, instance=None):
        return DataverseUserSerializer(context={'request': instance})

    def post(self, request):
        """Expects JSON. Given object_ids for OpenDPUser and DataverseHandoff objects,
        retrieve the user's information from Dataverse and create a DataverseUser"""

        # ----------------------------------
        # Validate the input
        # ----------------------------------
        print(f"data: {request.data}")

        dataverse_user_serializer = DataverseUserSerializer(data=request.data, context={'request': request})
        if not dataverse_user_serializer.is_valid():
            print("INVALID SERIALIZER")
            return JsonResponse(get_json_error(dataverse_user_serializer.errors),
                                status=status.HTTP_400_BAD_REQUEST)
        print(f"DataverseUserSerializer.validated_data: {dataverse_user_serializer.validated_data}")
        try:
            dataverse_user = dataverse_user_serializer.save()
        except DataverseHandoff.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No such DataVerse exists'})
        opendp_user = dataverse_user_serializer.validated_data.get('user')


        # ----------------------------------
        # Call the Dataverse API
        # ----------------------------------

        site_url = dataverse_user.dv_installation.dataverse_url
        api_general_token = dataverse_user.dv_general_token
        dataverse_client = DataverseClient(site_url, api_general_token)
        try:
            print(f"API token: {api_general_token}")
            dataverse_response = dataverse_client.get_user_info(user_api_token=api_general_token)
        except InvalidSchema:
            print("INVALID SCHEMA")
            return JsonResponse(get_json_error(f'The Site {site_url} is not valid'),
                                status=400)

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

    def put(self, request):
        """Update the Dataverse User. Expects JSON"""
        # ----------------------------------
        # Validate the input
        # ----------------------------------
        print(f"Query params: {request.query_params}")
        handoff_id = request.query_params.get('handoff_id')
        print(f"handoff_id: {handoff_id}")

        dataverse_handoff = get_object_or_404(DataverseHandoff, uuid=handoff_id)
        dataverse_user_serializer = DataverseUserSerializer(data=request.data, context={'request': request})
        if not dataverse_user_serializer.is_valid():
            return JsonResponse(get_json_error(dataverse_user_serializer.errors),
                                status=status.HTTP_400_BAD_REQUEST)

        opendp_user = dataverse_user_serializer[dv_static.KEY_DP_USER_ID]

        api_general_token = dataverse_handoff.apiGeneralToken
        site_url = dataverse_handoff.siteUrl

        dataverse_client = DataverseClient(site_url, api_general_token)
        try:
            dataverse_response = dataverse_client.get_user_info(user_api_token=api_general_token)
        except InvalidSchema:
            return JsonResponse({'error': f'Site {site_url} is not valid'}, status=400)

        if dataverse_response.success is not True:
            return JsonResponse({'error': dataverse_response.message}, status=400)

        try:
            handler = DataverseUserHandler(opendp_user.id, site_url, api_general_token, dataverse_response.__dict__)
            update_resp = handler.update_dataverse_user()
            if update_resp.success:
                updated_dv_user = update_resp.data
                updated_dv_user.save()
            else:
                return JsonResponse(get_json_error(update_resp.message))
        except DataverseResponseError as ex:
            print('--- DatDataverseResponseError', ex)
            return JsonResponse(get_json_error(ex), status=400)
            #return JsonResponse({'error': ex}, status=400)

        return JsonResponse(get_json_success('updated',
                                             data=dict(dv_user=updated_dv_user.object_id)),
                            status=201)
