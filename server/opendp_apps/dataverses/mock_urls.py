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
   path(f'{MOCK_API_PREFIX}/{MOCK_API_VERSION}/info/version',
        mock_dv_views.view_get_info_version,
        name='view_get_info_version'),

   path(f'{MOCK_API_PREFIX}/{MOCK_API_VERSION}/info/server',
        mock_dv_views.view_get_info_server,
        name='view_get_info_server'),

    path(f'{MOCK_API_PREFIX}/{MOCK_API_VERSION}/datasets/export',
         mock_dv_views.view_get_dataset_export,
         name='view_get_dataset_export'),

    re_path(r'^%s/%s/users/(?P<user_token>(\w|-){5,36})$' % (MOCK_API_PREFIX, MOCK_API_VERSION),
         mock_dv_views.view_get_user_info,
         name='view_get_user_info'),

]
