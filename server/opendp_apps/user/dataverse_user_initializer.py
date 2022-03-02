"""
Used when a Dataverse User is created or logging in.
This class is hooked into the OpenDP User register/login steps and does the following:

- Creates or updates a DataverseUser
    - Includes making an API call to Dataverse
-
"""
from json import JSONDecodeError
from requests.exceptions import InvalidSchema
from rest_framework import status as http_status

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.user.models import OpenDPUser, DataverseUser

from opendp_apps.dataverses.models import DataverseHandoff

from opendp_apps.dataverses.dataverse_client import DataverseClient
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses import static_vals as dv_static


class DataverseUserInitializer(BasicErrCheck):

    def __init__(self, opendp_user: OpenDPUser, dv_handoff_id: str):
        """Initialize the class with an OpenDPUser and DataverseHandoff.object_id"""
        self.opendp_user = opendp_user
        self.dv_handoff_id = dv_handoff_id

        # To be retrieved
        self.dv_handoff = None
        self.dv_user = None
        self.dv_file_info = None

        # http response code
        self.http_resp_code = None

        self.run_initializer_steps()

    def run_initializer_steps(self):
        """Run through the initializer steps which include:

        """
        if self.has_error():
            return

        # Retrieve the DataverseHandoff object
        #
        print('>> DataverseUserInitializer 1')
        if not self.retrieve_handoff_obj():
            return

        # Create or update the Dataverse user
        #
        print('>> DataverseUserInitializer 2')
        if not self.init_update_dv_user():
            return

        # Retrieve the latest Dataverse user info from Dataverse
        print('>> DataverseUserInitializer 3')
        if not self.retrieve_latest_dv_user_info():
            return

        #
        #
        print('>> DataverseUserInitializer 4')
        if not self.init_update_dv_file_info():
            return

        print('>> DataverseUserInitializer 5')


    def retrieve_handoff_obj(self) -> bool:
        """Retrieve the DataverseHandoff object"""
        if self.has_error():
            return False

        try:
            self.dv_handoff = DataverseHandoff.objects.get(object_id=self.dv_handoff_id)
        except DataverseHandoff.DoesNotExist:
            user_msg = f'Failed to retieve the DataverseHandoff object (id: {self.dv_handoff_id})'
            self.add_err_msg(user_msg)
            self.http_resp_code = http_status.HTTP_400_BAD_REQUEST
            return False

        return True

    def init_update_dv_user(self) -> bool:
        """Retrieve the DataverseUser object or Create one if it doesn't exist"""
        if self.has_error():
            return False

        try:
            self.dv_user = DataverseUser.objects.get(user=self.opendp_user,
                                                     dv_installation=self.dv_handoff.dv_installation)

        except DataverseUser.DoesNotExist:

            # initialize dv_user, don't save it yet
            self.dv_user = DataverseUser(user=self.opendp_user,
                                         dv_installation=self.dv_handoff.dv_installation,
                                         first_name=self.opendp_user.first_name,
                                         last_name=self.opendp_user.last_name,
                                         email=self.opendp_user.email,
                                         )

        # Update the dv_user with the latest token from the DataverseHandoff object
        #
        self.dv_user.dv_general_token = self.dv_handoff.apiGeneralToken
        self.dv_user.save()

        return True

    def retrieve_latest_dv_user_info(self) -> bool:
        """Use the API token to retrieve/updated the DataverseUser's latest info"""
        if self.has_error():
            return False

        # Init a DataverseClient object
        site_url = self.dv_handoff.dv_installation.dataverse_url
        dataverse_client = DataverseClient(site_url,
                                           self.dv_user.dv_general_token)

        try:
            dataverse_response = dataverse_client.get_user_info()
        except InvalidSchema:
            user_msg = f'The Site {site_url} is not valid'
            self.add_err_msg(user_msg)
            self.http_resp_code = http_status.HTTP_400_BAD_REQUEST
            return False
        except JSONDecodeError:
            user_msg = f'Error reading data from {site_url}'
            self.add_err_msg(user_msg)
            self.http_resp_code = http_status.HTTP_400_BAD_REQUEST
            return False

        if dataverse_response.success is not True:
            user_msg = dataverse_response.message
            self.add_err_msg(user_msg)
            self.http_resp_code = http_status.HTTP_400_BAD_REQUEST
            return False

        """
        Unpack the Dataverse response
        Example response
            {"status":"OK","data":{"id":11086,"identifier":"@jeff_prasad","displayName":"Jeff Prasad",
            "firstName":"Jeff","lastName":"Prasad","email":"jeff@some_uschool.edu",
            "superuser":false,"affiliation":"Some School",
            "persistentUserId":"https://some-persistent-id.com",
            "createdTime":"2000-01-01T05:00:00Z","lastApiUseTime":"2021-02-09T20:47:38Z",
            "authenticationProviderId":"shib"}}
        """
        try:
            dataverse_user_info_data = dataverse_response.__dict__.get('data', {})
            dataverse_user_info = dataverse_user_info_data.get('data', {})
            self.dv_user.persistent_id = dataverse_user_info['persistentUserId']
            self.dv_user.first_name = dataverse_user_info['firstName']
            self.dv_user.last_name = dataverse_user_info['lastName']
            self.dv_user.email = dataverse_user_info['email']
        except (AttributeError, KeyError) as ex:
            user_msg = f"Malformed Dataverse response when retrieving user info: {ex}"
            self.add_err_msg(user_msg)
            self.http_resp_code = http_status.HTTP_400_BAD_REQUEST
            return False

        self.dv_user.save()

        return True

    def init_update_dv_file_info(self) -> bool:
        """Create of update the DataverseFileInfo object"""
        if self.has_error():
            return False

        try:
            # Is there an existing DataverseFileInfo object?
            #
            qparams = dict(dataverse_file_id=self.dv_handoff.fileId,
                           dv_installation=self.dv_user.dv_installation)
            self.dv_file_info = DataverseFileInfo.objects.get(**qparams)

            # Verify that the OpenDP user is the DataverseFileInfo.creator
            #  If not, notify the user that the file is locked
            #
            if self.dv_file_info.creator != self.opendp_user:
                user_msg = 'This Dataverse file is locked by another user.'
                self.add_err_msg(user_msg)
                self.http_resp_code = http_status.HTTP_423_LOCKED
                return False

        except DataverseFileInfo.DoesNotExist:

            # Initialize a new DataverseFileInfo object
            self.dv_file_info = DataverseFileInfo(dv_installation=self.dv_user.dv_installation,
                                                  dataverse_file_id=self.dv_handoff.fileId,
                                                  dataset_doi=self.dv_handoff.datasetPid,
                                                  file_doi=self.dv_handoff.filePid,
                                                  dataset_schema_info=None,
                                                  file_schema_info=None,
                                                  creator=self.dv_user.user)

        # If the dataset_schema_info and file_schema_info exist, all set!
        #
        if self.dv_file_info.dataset_schema_info and self.dv_file_info.file_schema_info:
            if not self.dv_file_info.id:
                self.dv_file_info.save()    # shouldn't be needed...
            self.http_resp_code = http_status.HTTP_200_OK
            return True

        return self.retrieve_dv_file_info(self.dv_file_info)

    def retrieve_dv_file_info(self, dv_file_info: DataverseFileInfo) -> bool:
        """Use the Dataverse API to retrieve dataset schema info for the DataverseFileInfo object"""
        if self.has_error():
            return False

        site_url = self.dv_handoff.dv_installation.dataverse_url
        if not site_url:
            user_msg = 'The Dataverse url has not been set.'
            self.add_err_msg(user_msg)
            self.http_resp_code = http_status.HTTP_400_BAD_REQUEST
            return False

        params = self.dv_file_info.as_dict()
        params[dv_static.DV_PARAM_SITE_URL] = site_url

        # (1) Retrieve the JSON LD info
        client = DataverseClient(site_url, self.dv_user.dv_general_token)
        schema_org_resp = client.get_schema_org(self.dv_handoff.datasetPid)
        if schema_org_resp.status_code != 200:
            self.add_err_msg(schema_org_resp.message)
            self.http_resp_code = http_status.HTTP_400_BAD_REQUEST
            return False

        # (2) Retrieve the file specific info from the JSON-LD
        #
        schema_org_content = schema_org_resp.json()
        file_schema_resp = DataverseManifestParams.get_file_specific_schema_info(
                                    schema_org_content,
                                    self.dv_handoff.fileId,
                                    self.dv_handoff.filePid)

        if not file_schema_resp.success:
            self.add_err_msg(file_schema_resp.message)
            self.http_resp_code = http_status.HTTP_400_BAD_REQUEST
            return False

        # Update the DataverseFileInfo object
        #
        dv_file_info.dataset_schema_info = schema_org_content
        dv_file_info.file_schema_info = file_schema_resp.data

        # This will fail if the dataset_schema_info is malformed, use DOI as backup just in case:
        dv_file_info.name = dv_file_info.dataset_schema_info.get('name', dv_file_info.dataset_doi)

        # Save the DataverseFileInfo updates
        dv_file_info.save()

        self.dv_file_info = dv_file_info    # little messy here...

        self.http_resp_code = http_status.HTTP_201_CREATED
        return True


"""
from opendp_apps.dataverses.serializers import DataverseUserSerializer
from opendp_apps.user.models import OpenDPUser, DataverseUser
from opendp_apps.dataverses.models import DataverseHandoff

handoff_id = '45be40eb-86ed-4539-b5e8-e716dc71df6d'
dv_user_id = 'ed0bfb7e-c68a-42e0-b510-62ab3062ee40'
opendp_user_id = 'b579c31c-5ffa-411f-8830-31466d4cb641'

handoff = DataverseHandoff.objects.get(object_id=handoff_id)

dv_user = DataverseUser.objects.get(object_id=dv_user_id)

data = dict(user=opendp_user_id, dv_handoff=handoff_id)
s = DataverseUserSerializer(data=data)
s.is_valid()


s.update(
"""