from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views import View

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams

from opendp_apps.utils.view_helper import get_json_error, get_json_success

class DataverseUserInfoView(View):

    # These parameters are needed for the Dataverse API
    required_params = [dv_static.DV_PARAM_SITE_URL, dv_static.DV_API_GENERAL_TOKEN]

    def get(self, request):
        """(Not recommended) Pass the params as GET parameters
        Expected parameters: siteUrl, apiGeneralToken
        """
        mparams = DataverseManifestParams(request.GET,
                                          custom_required_params=self.required_params)

        return self.retrieve_user_info(mparams)


    def post(self, request):
        """
        Expected parameters: siteUrl, apiGeneralToken
        """
        mparams = DataverseManifestParams(request.POST,
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