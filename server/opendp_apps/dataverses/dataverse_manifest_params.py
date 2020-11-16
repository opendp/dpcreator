"""
Convenience class for assisting with handling Dataverse parameters sent by the external tools framework
"""
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.dataverses.dataverse_client import DataverseClient

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