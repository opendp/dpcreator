"""
Mimic the Dataverse urls for testing
- get user info
- get DDI
- download file
"""
from django.urls import path, re_path
from opendp_apps.dataverses import mock_dv_views

MOCK_API_PREFIX = 'api'
MOCK_API_VERSION = 'v1'

urlpatterns = [

    path(f'dataverse/incoming',
         mock_dv_views.view_dataverse_incoming,
         name='view_dataverse_incoming'),

    # Dataverse version and build numbers
    #
    path(f'{MOCK_API_PREFIX}/{MOCK_API_VERSION}/info/version',
        mock_dv_views.view_get_info_version,
        name='view_get_info_version'),

    # Dataverse server url
    #
    path(f'{MOCK_API_PREFIX}/{MOCK_API_VERSION}/info/server',
        mock_dv_views.view_get_info_server,
        name='view_get_info_server'),

    # Get DDI or schema.org dataset information
    #
    path(f'{MOCK_API_PREFIX}/{MOCK_API_VERSION}/datasets/export',
         mock_dv_views.view_get_dataset_export,
         name='view_get_dataset_export'),

    # Get user information
    #
    path(f'{MOCK_API_PREFIX}/{MOCK_API_VERSION}/users/:me',
         mock_dv_views.view_get_user_info,
         name='view_get_user_info'),

]

"""
https://dataverse.harvard.edu/api/v1/datasets/export?persistentId=doi:10.7910/DVN/OLD7MB&exporter=schema.org

schema.org
"""