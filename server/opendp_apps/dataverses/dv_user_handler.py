from django.shortcuts import get_object_or_404

from opendp_apps.model_helpers.basic_response import ok_resp, err_resp
from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.user.models import OpenDPUser, DataverseUser


class DataverseResponseError(Exception):
    pass


class DataverseUserHandler(object):

    def __init__(self, opendp_user_id, site_url, api_general_token, dataverse_response):

        self.dataverse_persistent_id, self.first_name, self.last_name, self.email = \
            self._unpack_dataverse_response(dataverse_response)
        self.site_url = site_url
        self.api_general_token = api_general_token
        self.opendp_user = get_object_or_404(OpenDPUser, id=opendp_user_id)

        self.registered_dataverse = get_object_or_404(RegisteredDataverse, dataverse_url=site_url)

    def _unpack_dataverse_response(self, dataverse_response):
        """Unpack the Dataverse response
        Example response
            {"status":"OK","data":{"id":11086,"identifier":"@jeff_prasad","displayName":"Jeff Prasad",
            "firstName":"Jeff","lastName":"Prasad","email":"jeff@some_uschool.edu",
            "superuser":false,"affiliation":"Some School",
            "persistentUserId":"https://some-persistent-id.com",
            "createdTime":"2000-01-01T05:00:00Z","lastApiUseTime":"2021-02-09T20:47:38Z",
            "authenticationProviderId":"shib"}}
        """
        try:
            dataverse_user_info_data = dataverse_response.get('data', {})
            dataverse_user_info = dataverse_user_info_data.get('data', {})
            dataverse_persistent_id = dataverse_user_info['persistentUserId']
            first_name = dataverse_user_info['firstName']
            last_name = dataverse_user_info['lastName']
            email = dataverse_user_info['email']
        except (AttributeError, KeyError) as ex:
            raise DataverseResponseError(f"Malformed Dataverse response: {ex}")

        return dataverse_persistent_id, first_name, last_name, email

    def create_dataverse_user(self):
        """
        """
        return DataverseUser(
            user=self.opendp_user,
            dv_installation=self.registered_dataverse,
            persistent_id=self.dataverse_persistent_id,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            dv_general_token=self.api_general_token
        )

    def update_dataverse_user(self):
        """Update the DataverseUser parameters"""
        try:
            dataverse_user = DataverseUser.objects.get(\
                                           user=self.opendp_user,
                                           dv_installation=self.registered_dataverse)
        except DataverseUser.DoesNotExist as ex:
            return err_resp('Dataverse user does not exist')

        # Update the parameters
        dataverse_user.persistent_id = self.dataverse_persistent_id
        dataverse_user.first_name = self.first_name
        dataverse_user.last_name = self.last_name
        dataverse_user.email = self.email

        # Save it!
        dataverse_user.save()

        return ok_resp(dataverse_user)
