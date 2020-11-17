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
from django.conf import settings

from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataverses import static_vals as dv_static

from opendp_apps.model_helpers.basic_response import ok_resp, err_resp
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.user.models import DataverseUser, OpenDPUser


class DataverseRequestHandler(BasicErrCheck):

    def __init__(self, manifest_params, user):
        """
        manifest_params - Django request.GET or python dict
        """
        self.mparams = DataverseManifestParams(manifest_params)
        if self.mparams.has_error():
            self.add_err_msg(self.mparams.get_error_message())
            return

        if not isinstance(user, OpenDPUser):
            self.add_err_msg('User must be an OpenDPUser object')
            return

        self.user = user

        self.user_info = None
        self.schema_info = None
        self.schema_info_for_file = None
        self.ddi_info = None

        self.dataverse_user = None

        self.process_dv_request()


    def process_dv_request(self):
        """
        Main function that walks through the process
        """
        if self.has_error():
            return

        if not self.retrieve_user_info():
            return

        if not self.retrieve_schema_org_info():
            return

        # (do more here)

        if not self.update_dataverse_user_info():
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
        if not schema_info.success:
            print(schema_info.message)
            self.add_err_msg(schema_info.message)
            return False
        self.schema_info = schema_info.data

        # (2) Retrieve the file specific info from the JSON-LD
        #
        file_info = self.mparams.get_file_specific_schema_info(self.schema_info)
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

        print('---   hahahah -----')
        print(type(self.user_info))
        print(self.user_info)

        dv_persistent_id = self.user_info.get(dv_static.DV_PERSISTENT_USER_ID)
        if not dv_persistent_id:
            user_msg = (f'Could not find "{dv_static.DV_PERSISTENT_USER_ID}"'
                        f' in the Dataverse user info.')
            self.add_err_msg(user_msg)
            return False

        self.dataverse_user, _created = DataverseUser.objects.get_or_create(
                                            user=self.user,
                                            dv_installation=self.mparams.siteUrl,
                                            persistent_id=dv_persistent_id)

        # update params, if needed
        self.dataverse_user.email = self.user_info.get(dv_static.DV_EMAIL)
        self.dataverse_user.dataverse_first_name = self.user_info.get(dv_static.DV_FIRST_NAME)
        self.dataverse_user.dataverse_last_name = self.user_info.get(dv_static.DV_LAST_NAME)

        self.dataverse_user.save()
        return True


""" 
#DataverseUser
(TimestampedModelWithUUID):
user = models.ForeignKey(OpenDPUser,
                         on_delete=models.PROTECT)

dv_installation = models.CharField(max_length=255)
persistent_id = models.CharField(max_length=255)  # Persistent DV user id within an installation

dataverse_email = models.EmailField(max_length=255, blank=True)
dataverse_first_name = models.CharField(max_length=255, blank=True)
dataverse_last_name = models.CharField(max_length=255, blank=True)
"""