"""
Mimic the Dataverse urls for testing
- get user info
- get DDI
- download file
"""

from rest_framework import routers

from opendp_apps.dataverses.views import DataverseHandoffView

router = routers.DefaultRouter()
router.register(r'dataverses/handoff',
                DataverseHandoffView,
                basename='view_dataverse_handoff')
