from django.urls import path, re_path
from opendp_apps.dataverses.view_dataverse_user_info import DataverseUserInfoView
from opendp_apps.dataverses.view_dataverse_dataset_info import DataverseDatasetInfoView

# This may move to DRF..
urlpatterns = [

    # Retrieve User Information from a Dataverse Installation
    path(f'dv-info/get-user-info/',
         DataverseUserInfoView.as_view(),
         name='view_get_dv_user_info'),

    # Retrieve DV Dataset and DV File Metadata from a Dataverse Installation
    path(f'dv-info/get-dataset-info/',
         DataverseDatasetInfoView.as_view(),
         name='view_get_dv_dataset_info'),

]
