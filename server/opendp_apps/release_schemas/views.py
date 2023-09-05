import logging

from django.conf import settings
from rest_framework import viewsets

from opendp_apps.release_schemas.models import ReleaseInfoSchema
from opendp_apps.release_schemas.serializers import ReleaseSchemaSerializer

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class ReleaseSchemaView(viewsets.ModelViewSet):
    """
    API endpoint to list AnalysisPlans, but w/o information such as variable_info and dp_statistics.
    This listing is used to populate tables that include AnalysisPlans with published ReleaseInfo object where the logged in user is not the analyst or dataset creator.
    """
    serializer_class = ReleaseSchemaSerializer
    lookup_field = 'version'
    http_method_names = ['get']

    def get_queryset(self):
        """
        AnalysisPlans for the currently authenticated user.
        """
        return ReleaseInfoSchema.objects.filter(is_published=True)
