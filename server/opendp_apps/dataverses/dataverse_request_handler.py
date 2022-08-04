"""
Handle an incoming Dataverse request which includes
    external tool parameters in the url

Completes the following steps:

100 - Checks for correct Dataverse params
200 - Retrieves user info via the API
300 - Retrieves dataset schema info via the API (JSON LD)
400 - Update user info
500 - Check if file exists in OpenDP App
    - Yes
        - Has a release been created? Yes -> exit
        - Is the file "locked"; Yes -> exit  (What does "locked" mean?)
        - Has the analysis been submitted for execution?  Yes -> update tokens (for deposit),
        - Is the workflow in process? Update tokens, re-retrieve DDI if needed, reconnect to old workflow
    - No
        - Retrieve the DDI
        - Create file-related objects


"""

from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
# from opendp_apps.model_helpers.basic_response import ok_resp, err_resp
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.user.models import DataverseUser, OpenDPUser


class DataverseRequestHandler(BasicErrCheck):

    def __init__(self, manifest_params, user):
        """
        manifest_params - Django request.GET or python dict
        """
        self.mparams = DataverseManifestParams(manifest_params)

        # In memory data
        self.user_info = None
        self.schema_info = None
        self.schema_info_for_file = None
        self.ddi_info = None

        # References to Django model instances
        self.dataverse_user = None
        self.dataverse_file_info = None

        if self.mparams.has_error():
            self.add_err_msg(self.mparams.get_error_message())
            return

        if not isinstance(user, OpenDPUser):
            self.add_err_msg('User must be an OpenDPUser object')
            return

        self.user = user

        self.process_dv_request()

    def process_dv_request(self):
        """
        Main function that walks through the process
        """
        if self.has_error():
            return

        # Retrieve minimal data to do work
        #
        if not self.retrieve_user_info():
            return

        if not self.retrieve_schema_org_info():
            return

        # DDI...

        # Yes, we have all the necessary data, start updating models/tables
        #
        if not self.update_dataverse_user_info():
            return

        if not self.update_dataverse_file_info():
            return

    def retrieve_user_info(self):
        """
        User the DV API to retrieve user info
        """
        if self.has_error():
            return False

        user_info = self.mparams.get_user_info()
        if not user_info.success:
            self.add_err_msg(user_info.message)
            return False

        if isinstance(user_info.data, dict):
            if 'data' in user_info.data:
                self.user_info = user_info.data.get('data')
                return True
            else:
                user_msg = '"data" key not found in user information from Dataverse API'
        else:
            user_msg = 'user_info.data must be a Python dict'

        self.add_err_msg(user_msg)
        return False

    def retrieve_schema_org_info(self):
        """
        User the DV API to retrieve schema.org info about the dataset
        """
        if self.has_error():
            return False

        # (1) Retrieve the JSON LD info
        #
        schema_info = self.mparams.get_schema_org()
        if schema_info.status_code >= 400:
            self.add_err_msg(schema_info.message)
            return False
        self.schema_info = schema_info.json()

        # (2) Retrieve the file specific info from the JSON-LD
        #
        file_info = self.mparams.retrieve_file_specific_info(self.schema_info)
        if not file_info.success:
            self.add_err_msg(file_info.message)
            return False

        self.schema_info_for_file = file_info.data
        return True

    def update_dataverse_user_info(self):
        """
        Create or update the DataverseUser related to the OpenDP user
        """
        if self.has_error():
            return False

        test_data = { \
            'id': 11086,
            'identifier': '@raman_prasad',
            'displayName': 'Raman Prasad',
            'firstName': 'Raman',
            'lastName': 'Prasad', 'email': 'raman_prasad@harvard.edu', 'superuser': False,
            'affiliation': 'Harvard University',
            'persistentUserId': 'https://fed.huit.harvard.edu/idp/shibboleth|0e459e6d562ec7e5@harvard.edu',
            'createdTime': '2000-01-01T05:00:00Z', 'lastApiUseTime': '2020-11-16T21:52:14Z',
            'authenticationProviderId': 'shib'}

        dv_persistent_id = self.user_info.get(dv_static.DV_PERSISTENT_USER_ID)
        if not dv_persistent_id:
            user_msg = (f'Could not find "{dv_static.DV_PERSISTENT_USER_ID}"'
                        f' in the Dataverse user info.')
            self.add_err_msg(user_msg)
            return False

        self.dataverse_user, _created = DataverseUser.objects.get_or_create(
            user=self.user,  # logged in user
            dv_installation=self.mparams.registered_dataverse,  # from GET request
            persistent_id=dv_persistent_id)  # from User Info

        # update params, if needed
        self.dataverse_user.email = self.user_info.get(dv_static.DV_EMAIL)
        self.dataverse_user.first_name = self.user_info.get(dv_static.DV_FIRST_NAME)
        self.dataverse_user.last_name = self.user_info.get(dv_static.DV_LAST_NAME)

        self.dataverse_user.save()
        return True

    def update_dataverse_file_info(self):
        """
        Retrieve or create a DataverseFileInfo object
        """
        query_params = dict(source=DataverseFileInfo.SourceChoices.Dataverse,
                            dv_installation=self.mparams.registered_dataverse,
                            dataverse_file_id=self.mparams.fileId
                            )
        defaults = dict(creator=self.user,  # logged in user, OpenDP user
                        name=self.schema_info_for_file.get(dv_static.SCHEMA_KEY_NAME,
                                                           f'DV file {self.mparams.filePid}'),
                        dataset_doi=self.mparams.datasetPid,
                        file_doi=self.mparams.filePid if self.mparams.filePid else '')

        dv_file_info, _created = DataverseFileInfo.objects.get_or_create(**query_params, defaults=defaults)

        self.dataverse_file_info = dv_file_info

        return True

        # Need to check depositor status, is file in use, is there a release, etc...
