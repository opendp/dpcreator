from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views import View

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams

from opendp_apps.utils.view_helper import get_json_error, get_json_success

class DataverseDatasetInfoView(View):
    """API to retrieve Dataverse Dataset Information"""

    # These parameters are needed for the Dataverse API
    required_params = [dv_static.DV_PARAM_SITE_URL,
                       dv_static.DV_API_GENERAL_TOKEN,
                       dv_static.DV_PARAM_DATASET_PID,
                       #dv_static.DV_PARAM_FILE_ID,
                       #dv_static.DV_PARAM_FILE_PID
                       ]

    def get(self, request):
        """(Not recommended) Pass the params as GET parameters
        Expected parameters: siteUrl, apiGeneralToken
        """
        mparams = DataverseManifestParams(request.GET,
                                          custom_required_params=self.required_params)

        return self.get_dataset_info(mparams)


    def post(self, request):
        """
        Expected parameters: siteUrl, apiGeneralToken
        """
        mparams = DataverseManifestParams(request.POST,
                                          custom_required_params=self.required_params)

        return self.get_dataset_info(mparams)


    def get_dataset_info(self, mparams):
        """
        Retrieve the dataset's JSON-LD information from Dataverse

        mparams - instance of DataverseManifestParams
        """
        # Fail if this isn't an instance of DataverseManifestParams
        assert isinstance(mparams, DataverseManifestParams)

        # Are all the required parameters avaiable?
        if mparams.has_error():
            return JsonResponse(get_json_error(mparams.get_error_message()))

        # (1) Retrieve the schema.org information from Dataverse
        #
        schema_info_resp = mparams.get_schema_org()
        if not schema_info_resp.success:
            return JsonResponse(get_json_error(schema_info_resp.message))

        schema_info = schema_info_resp.data
        print('schema_info', schema_info)

        # (2) Retrieve the file specific info from the schema.org information
        #
        file_info_resp = mparams.get_file_specific_schema_info(schema_info)
        if not file_info_resp.success:
            return JsonResponse(get_json_error(file_info_resp.message))


        file_info = file_info_resp.data

        resp_info = dict(dataset_schema=schema_info,
                         file_info=file_info)

        return JsonResponse(get_json_success(resp_info))
