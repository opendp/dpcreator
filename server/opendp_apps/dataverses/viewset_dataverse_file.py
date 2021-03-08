from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import permissions  # , authentication, viewsets
from rest_framework import serializers

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams

from opendp_apps.utils.view_helper import get_json_error, get_json_success


class DataverseRetrieveFileInputSerializer(serializers.Serializer):
    """API Input parameters"""
    siteUrl = serializers.URLField(label='Dataverse url',
                                   help_text='Example: https://dataverse.harvard.edu')

    apiSensitiveDataReadToken = serializers.CharField(max_length=255,
                                            label='Dataverse Sensitive Data API Token',
                                            help_text=('Reference: https://guides.dataverse.org'
                                                       '/en/latest/user/account.html#api-token'))

    fileId = serializers.IntegerField(required=True,
                                      label='Dataverse File Id',
                                      help_text='Example: 4034504')


class DataverseRetrieveFileView(APIView):
    """API to retrieve Dataverse Dataset Information"""

    # These parameters are needed for the Dataverse API
    required_params = [dv_static.DV_PARAM_SITE_URL,
                       dv_static.DV_API_SENSITIVE_DATA_READ_TOKEN,
                       dv_static.DV_PARAM_FILE_ID]

    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        """
        Expected parameters:
        - dv_static.DV_PARAM_SITE_URL
        - dv_static.DV_API_SENSITIVE_DATA_READ_TOKEN,
        - dv_static.DV_PARAM_FILE_ID
        """
        mparams = DataverseManifestParams(request.POST.dict(),
                                          custom_required_params=self.required_params)

        return self.get_dataset_info(mparams)

    def get_dataverse_file(self, mparams):
        """
        Retrieve the dataset's JSON-LD information from Dataverse

        mparams - instance of DataverseManifestParams
        """
        # Fail if this isn't an instance of DataverseManifestParams
        assert isinstance(mparams, DataverseManifestParams)

        # Are all the required parameters avaiable?
        if mparams.has_error():
            return JsonResponse(get_json_error(mparams.get_error_message()))

        file_info_resp = mparams.download_file(schema_info)
        if not file_info_resp.success:
            return JsonResponse(get_json_error(file_info_resp.message))

        file_info = file_info_resp.data

        resp_info = dict(dataset_schema=schema_info,
                         file_info=file_info)

        return JsonResponse(get_json_success(resp_info))

    def get_serializer(self):
        return DataverseDatasetInputSerializer()


"""
import requests

payload = {"fileId": 4034504, "siteUrl": "https://dataverse.harvard.edu/", "apiGeneralToken": "some-other-token", "datasetPid": "doi:10.7910/DVN/B7DHBK", "filePid": "doi:10.7910/DVN/B7DHBK/BSNYLQ"}

r = requests.post('http://0.0.0.0:8000/api/dv-dataset/', data=payload); print(r.text)

print(f'status: {r.status_code}')
print(f'text: {r.text}')

"""