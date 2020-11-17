"""
Convenience class for assisting with handling Dataverse parameters sent by the external tools framework
- Includes functions to make Dataverse API calls and process the results
"""
from django.http import QueryDict

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.dataverse_client import DataverseClient

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp


class DataverseManifestParams(BasicErrCheck):

    CORE_PARAMS = ['fileId', 'siteUrl', 'datasetPid',]
    OPTIONAL_PARAMS = ['filePid',]
    TOKENS = ['apiGeneralToken', 'apiSensitiveDataReadToken', ]

    REQUIRED_PARAMS = CORE_PARAMS + TOKENS
    ALL_PARAMS = CORE_PARAMS + TOKENS + OPTIONAL_PARAMS

    def __init__(self, incoming_params, **kwargs):
        """
        Dynamically set fields based on the static variables
        """
        if not (isinstance(incoming_params, dict) or \
                isinstance(incoming_params, QueryDict)):
            self.add_error_message(('"incoming_params" must be python dict or'
                                    ' Django QueryDict object (e.g. request.GET)'))
            return

        self.missing_params = []

        for param in self.ALL_PARAMS:
            val = incoming_params.get(param)
            if isinstance(val, str) and val.strip() == '':
                val = None

            if val is None and param in self.REQUIRED_PARAMS:
                self.missing_params.append(param)

            self.__dict__[param] = val

        self.check_params()


    def check_params(self):
        """
        Check required params
        """
        if self.missing_params:
            if len(self.missing_params) == 1:
                user_msg = 'This required parameter is missing: %s' % (', '.join(self.missing_params))
            else:
                user_msg = 'These required parameters are missing: %s' % (', '.join(self.missing_params))
            self.add_err_msg(user_msg)
            return

    def get_schema_org(self):
        """
        Get the schema org content of the dataset
        """
        client = DataverseClient(self.siteUrl, self.apiGeneralToken)

        schema_org_content = client.get_schema_org(self.datasetPid)

        return schema_org_content


    def get_user_info(self):
        """
        Return the user information
        """
        client = DataverseClient(self.siteUrl, self.apiGeneralToken)

        user_info = client.get_user_info(self.apiGeneralToken)
        print('user_info', user_info)

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

        for file_info in full_schema_info[dv_static.SCHEMA_KEY_DISTRIBUTION]:
            if dv_static.SCHEMA_KEY_CONTENTURL in file_info:
                url_ending = f'/{self.fileId}'
                if file_info[dv_static.SCHEMA_KEY_CONTENTURL].endswith(url_ending):
                    return ok_resp(file_info)

        return err_resp(f'Info for fileId "{self.fileId}" not found in the schema')
