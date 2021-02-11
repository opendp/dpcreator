from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import permissions  #,authentication,  viewsets
from rest_framework import serializers

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams

from opendp_apps.utils.view_helper import get_json_error, get_json_success


class DaverseUserInputSerializer(serializers.Serializer):
    """API Input parameters"""
    siteUrl = serializers.URLField(label='Dataverse url',
                                   help_text='Example: https://dataverse.harvard.edu')

    apiGeneralToken = serializers.CharField(max_length=255,
                                            label='Dataverse API Token',
                                            help_text=('Reference: https://guides.dataverse.org'
                                                       '/en/latest/user/account.html#api-token'))

class DataverseUserInfoView(APIView):
    """API to retrieve Dataverse User Information.
    Required param"""

    # These parameters are needed for the Dataverse API
    required_params = [dv_static.DV_PARAM_SITE_URL,
                       dv_static.DV_API_GENERAL_TOKEN]

    # Remove this for now, so Vue app can call it before user logs in
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        """
        Expected parameters:
        - dv_static.DV_PARAM_SITE_URL
        - dv_static.DV_API_GENERAL_TOKEN
        """
        mparams = DataverseManifestParams(request.POST.dict(),
                                          custom_required_params=self.required_params)

        return self.retrieve_user_info(mparams)


    def retrieve_user_info(self, mparams):
        """
        Using the Dataverse site url and token in DataverseManifestParams,
        retrieve the user info from Dataverse

        mparams - instance of DataverseManifestParams
        """
        # Fail if this isn't an instance of DataverseManifestParams
        assert isinstance(mparams, DataverseManifestParams)

        if mparams.has_error():
            return JsonResponse(get_json_error(mparams.get_error_message()))

        user_info = mparams.get_user_info()
        if not user_info.success:
            return JsonResponse(get_json_error(user_info.message))

        if isinstance(user_info.data, dict):
            if 'data' in user_info.data:
                return JsonResponse(get_json_success('Success',
                                                     data=user_info.data.get('data')))
            else:
                user_msg = '"data" key not found in user information from Dataverse API'
        else:
            user_msg = 'user_info.data must be a Python dict'

        return JsonResponse(get_json_error(user_msg))

    def get_serializer(self):
        return DaverseUserInputSerializer()


"""
import requests

payload = {"siteUrl": "https://dataverse.harvard.edu/", "apiGeneralToken": "(dataverse-token)"} 
r = requests.post('http://0.0.0.0:8000/api/dv-user/', data=payload)
                  
print(f'status: {r.status_code}')
print(f'text: {r.text}')

"""