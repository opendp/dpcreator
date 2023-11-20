import logging

from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from opendp_apps.utils.view_helper import get_json_error
from rest_framework import status

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
    lookup_value_regex = '[\w.]+'
    http_method_names = ['get']

    def get_queryset(self):
        """
        AnalysisPlans for the currently authenticated user.
        """
        return ReleaseInfoSchema.objects.filter(is_published=True)


    @action(detail=False, methods=['GET'], url_path='latest')
    def latest(self, request):
        """
        Retrieve the JSON schema for a given version
        Example: http://127.0.0.1:8000/api/release-download/0-2-0/json/
        """
        release_schema = ReleaseInfoSchema.get_latest_schema()
        if release_schema is not None:
            serializer = ReleaseSchemaSerializer(release_schema)  # serialize the data
            logger.info(f"AnalysisPlan created: {serializer.data}")
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(get_json_error('A published schema was not found'),
                        status=status.HTTP_404_NOT_FOUND)

