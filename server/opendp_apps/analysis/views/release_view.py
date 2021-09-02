from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response

from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis.serializers import DPStatisticSerializer, ReleaseInfoSerializer, AnalysisPlanSerializer, \
    ReleaseInfoSerializer
from opendp_apps.utils.view_helper import get_object_or_error_response


class ReleaseView(viewsets.ViewSet):

    statistics = ReleaseInfoSerializer()
    analysis_plan = AnalysisPlanSerializer()

    def create(self, request, *args, **kwargs):
        """
        Run validation for a list of release requests
        """
        analysis_plan_id = request.data.get('analysis_plan_id')
        dp_statistics = request.data.get('dp_statistics')
        # analysis_plan = get_object_or_error_response(AnalysisPlan, object_id=analysis_plan_id)
        release_info_serializer = ReleaseInfoSerializer(data={'dp_statistics': dp_statistics})
        if not release_info_serializer.is_valid():
            raise Exception("Invalid DPStatistics objects")
        stats_valid = release_info_serializer.save()
        return Response({'valid': stats_valid})

