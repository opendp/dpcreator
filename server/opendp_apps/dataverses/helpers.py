from django.shortcuts import get_object_or_404

from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.user.models import OpenDPUser, DataverseUser


class DataverseResponseError(Exception):
    pass


def create_dataverse_user(opendp_user_id, site_url, api_general_token, dataverse_response):
    """
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

    opendp_user = get_object_or_404(OpenDPUser, id=opendp_user_id)
    registered_dataverse = get_object_or_404(RegisteredDataverse, dataverse_url=site_url)
    return DataverseUser(
        user=opendp_user,
        dv_installation=registered_dataverse,
        persistent_id=dataverse_persistent_id,
        email=email,
        first_name=first_name,
        last_name=last_name,
        dv_general_token=api_general_token
    )
