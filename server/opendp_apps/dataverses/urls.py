from django.urls import path, re_path
from opendp_apps.dataverses.views import DataverseUserInfoView
# This may move to DRF..
urlpatterns = [

    path(f'dv-info/get-user-info',
         DataverseUserInfoView.as_view(),
         name='view_get_dv_user_info'),
]