"""
Convenience class for assisting with handling Dataverse parameters sent by the external tools framework
- Includes functions to make Dataverse API calls and process the results
"""
from django.http import QueryDict

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.dataverse_client import DataverseClient
from opendp_apps.dataverses.forms import DataverseParamsSiteUrlForm

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp

class DataverseManifestParams(BasicErrCheck):

    def __init__(self, incoming_params, **kwargs):
        """
        Set initial params
        """
        if not (isinstance(incoming_params, dict) or \
                isinstance(incoming_params, QueryDict)):
            self.add_error_message(('"incoming_params" must be python dict or'
                                    ' Django QueryDict object (e.g. request.GET)'))
            return

        self.custom_required_params = kwargs.get('custom_required_params')
        # print(incoming_params)
        self.fileId = self.format_param(incoming_params.get(dv_static.DV_PARAM_FILE_ID))
        self.siteUrl = self.format_param(incoming_params.get(dv_static.DV_PARAM_SITE_URL))
        self.datasetPid = self.format_param(incoming_params.get(dv_static.DV_PARAM_DATASET_PID))
        self.filePid = self.format_param(incoming_params.get(dv_static.DV_PARAM_FILE_PID))
        self.apiGeneralToken = self.format_param(incoming_params.get(dv_static.DV_API_GENERAL_TOKEN))
        self.apiSensitiveDataReadToken = self.format_param(incoming_params.get(dv_static.DV_API_SENSITIVE_DATA_READ_TOKEN))

        self.registerd_dataverse = None # RegisteredDataverse connected with self.siteUrl

        self.check_required_params()

    def format_param(self, val):
        """
        Convert empty strings to None
        """
        if isinstance(val, str):
            val = val.strip()
            if not val:
                val = None
        return val

    def check_required_params(self):
        """
        Check that required params are set
        """
        missing_params = []
        if self.custom_required_params:
            # custom required parameters
            required_params = self.custom_required_params
        else:
            # default required parameters
            required_params = (list(set(dv_static.DV_ALL_PARAMS) - set(dv_static.DV_OPTIONAL_PARAMS)))

        # If the siteUrl is required, check that it's connected to a RegisteredDataverse
        #
        if dv_static.DV_PARAM_SITE_URL in required_params:
            f = DataverseParamsSiteUrlForm({'siteUrl': self.siteUrl})
            if not f.is_valid():
                user_msg = (f'This "{dv_static.DV_PARAM_SITE_URL}" was not connected'
                            f' to a registered Dataverse: {self.siteUrl}')
                self.add_err_msg(user_msg)
                return
            else:
                self.registerd_dataverse = f.cleaned_data[dv_static.DV_PARAM_SITE_URL]

        for param in required_params:
            if not self.__dict__.get(param):
                missing_params.append(param)

        if missing_params:
            if len(missing_params) == 1:
                user_msg = 'This required parameter is missing: %s' % (', '.join(missing_params))
            else:
                user_msg = 'These required parameters are missing: %s' % (', '.join(missing_params))

            self.add_err_msg(user_msg)
            return



    def get_schema_org(self):
        """
        Via the Dataverse API, get the schema org content of the dataset
        """
        client = DataverseClient(self.siteUrl, self.apiGeneralToken)

        schema_org_content = client.get_schema_org(self.datasetPid)

        return schema_org_content


    def get_user_info(self):
        """
        Via the Dataverse API, return the user information
        """
        client = DataverseClient(self.siteUrl, self.apiGeneralToken)

        user_info = client.get_user_info(self.apiGeneralToken)

        return user_info

    def get_file_specific_schema_info(self, full_schema_info):
        """
        Navigate the JSON-LD schema.org info to retrieve file specific info
       "distribution":[
          {
             "@type":"DataDownload",
             "name":"Crisis.PDF",
             "fileFormat":"application/pdf",
             "contentSize":677112,
             "description":"Article related to this study: The Supreme Court During Crisis: How War Affects Only Nonwar Cases",
             "@id":"https://doi.org/10.7910/DVN/OLD7MB/PZPDJF",
             "identifier":"https://doi.org/10.7910/DVN/OLD7MB/PZPDJF",
             "contentUrl":"https://dataverse.harvard.edu/api/access/datafile/101646"
          },
          (etc)
        ]
        """
        if not isinstance(full_schema_info, dict):
            return err_resp('"full_schema_info" must be a Python dict')

        if not dv_static.SCHEMA_KEY_DISTRIBUTION in full_schema_info:
            return err_resp(f'"{dv_static.SCHEMA_KEY_DISTRIBUTION}" not found in the schema')

        url_ending_1 = f'/{self.fileId}'
        file_doi = self.filePid.split(':')[-1] if self.filePid else None

        for file_info in full_schema_info[dv_static.SCHEMA_KEY_DISTRIBUTION]:

            # Try to match the the /{fileId} id to the end of the contentURL
            #   example "contentUrl": https://dataverse.harvard.edu/api/access/datafile/101646"
            #
            if dv_static.SCHEMA_KEY_CONTENTURL in file_info:
                content_url = file_info[dv_static.SCHEMA_KEY_CONTENTURL]
                if content_url and content_url.endswith(url_ending_1):
                    return ok_resp(file_info)

            # If there's there's a file DOI, try to match it with the identifier
            #
            #   example "identifier": "https://doi.org/10.7910/DVN/B7DHBK/BSNYLQ"
            #
            if file_doi and dv_static.SCHEMA_KEY_IDENTIFIER in file_info:
                identifier = file_info[dv_static.SCHEMA_KEY_IDENTIFIER]
                if identifier and identifier.endswith(file_doi):
                    return ok_resp(file_info)

        if self.fileId:
            user_msg = f'Did not find fileId "{self.fileId}"'
        elif file_info:
            user_msg = f'Did not find file DOI "{file_doi}"'
        else:
            user_msg = ''

        return err_resp(f'Info for file not found in the schema. {user_msg}')
