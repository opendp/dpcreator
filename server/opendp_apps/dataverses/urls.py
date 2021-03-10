"""
Mimic the Dataverse urls for testing
- get user info
- get DDI
- download file
"""
from django.urls import path, re_path
from opendp_apps.dataverses import views

urlpatterns = [

    path(f'handoff',
         views.view_dataverse_handoff,
         name='view_dataverse_handoff'),
]

"""
https://dataverse.harvard.edu/api/v1/datasets/export?persistentId=doi:10.7910/DVN/OLD7MB&exporter=schema.org

schema.org
"""
