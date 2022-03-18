"""
This API endpoint is used to pass **Non-private** variable to the Vue frontend.
- Examples include keys such as a non-sensitive Google ID (used for Auth) and
    an Adobe ID (for PDF embedding)
- Workaround note: Given the current build process which puts compiled Vue .js
    into a Docker image, this API endpoint allows server side environment variables
    to be passed to the UI--variables that differ depending on deployment and may
    be changed in kubernetes config files.
- ref: https://stackoverflow.com/questions/13603027/django-rest-framework-non-model-serializer

"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets

from django.conf import settings

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.content_pages import static_vals as cstatic

class VueSettingsView(viewsets.ViewSet):
    """
    Simple API call returning non-sensitive environment varaibles
    """
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        """Return selected environment variables that may differ depending on deployment"""
        settings_info = {
            cstatic.KEY_VUE_APP_GOOGLE_CLIENT_ID: settings.VUE_APP_GOOGLE_CLIENT_ID,
            cstatic.KEY_VUE_APP_ADOBE_PDF_CLIENT_ID: settings.VUE_APP_ADOBE_PDF_CLIENT_ID,
            cstatic.KEY_VUE_APP_WEBSOCKET_PREFIX: settings.VUE_APP_WEBSOCKET_PREFIX,
            'TOTAL_EPSILON_MIN': settings.TOTAL_EPSILON_MIN,  # 1/1000
            'TOTAL_EPSILON_MAX': settings.TOTAL_EPSILON_MAX,  # 1.0
            'MAX_EPSILON_OFFSET': astatic.MAX_EPSILON_OFFSET, # 10**-14
            # 'MAX_EPSILON_OFFSET': format(astatic.MAX_EPSILON_OFFSET, '.14f') # 10**-14
        }

        response = Response(settings_info, status=status.HTTP_200_OK)

        return response