"""
Mimic the Dataverse urls for testing
- get user info
- get DDI
- download file
"""
from django.urls import path, re_path
from opendp_apps.dataverses import views, mock_dv_views

MOCK_API_PREFIX = 'api'
MOCK_API_VERSION = 'v1'

urlpatterns = [

    re_path(f'dv-info/as-dict/(?P<object_id>[0-9a-f-]+)',
            views.view_as_dict,
            name='view_as_dict'),

    path(f'dataverse/incoming-test-1',
         mock_dv_views.view_dataverse_incoming_1,
         name='view_dataverse_incoming_1'),

    path(f'dataverse/incoming-test-2',
         mock_dv_views.view_dataverse_incoming_2,
         name='view_dataverse_incoming_2'),

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