from http import HTTPStatus

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from rest_framework.views import APIView

from opendp_apps.dataverses.dataverse_client import DataverseClient
from opendp_apps.dataverses.helpers import create_dataverse_user, DataverseResponseError
from opendp_apps.utils.view_helper import get_json_error, get_json_success
from opendp_apps.dataverses.models import ManifestTestParams, RegisteredDataverse


# Limit this to superusers!!!
@user_passes_test(lambda u: u.is_superuser)
def view_as_dict(request, object_id):
    """Return the ManifestTestParams in JSON format"""
    mparams = ManifestTestParams.objects.filter(object_id=object_id).first()
    if not mparams:
        return JsonResponse(get_json_error('Object not found'), status=HTTPStatus.NOT_FOUND)

    return JsonResponse(get_json_success('Success', data=mparams.as_dict()))


class DataverseUserView(APIView):

    def post(self, request, opendp_user_id, site_url, api_general_token):
        dataverse_client = DataverseClient(site_url, api_general_token)
        dataverse_response = dataverse_client.get_user_info(user_api_token=api_general_token)

        if dataverse_response.get('success') is not True:
            return JsonResponse({'error': dataverse_response.get('message')}, status=400)

        try:
            new_dv_user = create_dataverse_user(opendp_user_id, site_url, api_general_token, dataverse_response)
            dv_user = new_dv_user.save()
        except DataverseResponseError as ex:
            return JsonResponse({'error': ex}, status=400)

        return JsonResponse({'dv_user': dv_user.id})

    def put(self, request, opendp_user_id):
        pass

    def get(self, request, *args, **kwargs):
        pass

