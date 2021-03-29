"""
Mimic the Dataverse urls for testing
- get user info
- get DDI
- download file
"""
from django.urls import path, re_path
from opendp_apps.dataverses import views

from rest_framework import routers, serializers

from opendp_apps.dataverses.views import ViewDataverseHandoff, ViewHandoffParams

router = routers.DefaultRouter()
router.register(r'dataverses/handoff',
                ViewDataverseHandoff,
                basename='view_dataverse_handoff')
router.register(r'dataverses/view-handoff-params',
                ViewHandoffParams,
                basename='view_handoff_params_test')


"""
https://dataverse.harvard.edu/api/v1/datasets/export?persistentId=doi:10.7910/DVN/OLD7MB&exporter=schema.org

schema.org
"""
