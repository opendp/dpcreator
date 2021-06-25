"""
!DANGER!: These urlpatterns should only be used in test.
Please read server/opendp_project/settings/cypress_settings for an explanation
"""
from django.urls import path, include

from opendp_project.urls import urlpatterns
from opendp_apps.cypress_utils.check_setup import are_cypress_settings_in_place

if are_cypress_settings_in_place:
    urlpatterns = [path('cypress-tests/', include('opendp_apps.cypress_utils.urls'))] \
                  + urlpatterns
