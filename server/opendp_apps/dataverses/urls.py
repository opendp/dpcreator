"""
Mimic the Dataverse urls for testing
- get user info
- get DDI
- download file
"""
from django.urls import path, re_path
from opendp_apps.dataverses import views

from rest_framework import routers, serializers

from opendp_apps.dataverses.views import DataverseHandoffView

router = routers.DefaultRouter()
router.register(r'dataverses/handoff',
                DataverseHandoffView,
                basename='view_dataverse_handoff')

