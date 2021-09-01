from django.http import JsonResponse
from rest_framework import viewsets

from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis.serializers import DPStatisticSerializer, ReleaseSerializer, AnalysisPlanSerializer, \
    ReleaseInfoSerializer
from opendp_apps.utils.view_helper import get_object_or_error_response


class BaseStepUpdaterView(viewsets.ViewSet):
    """
    Idea: keep next_step as view property to tell each endpoint how
    to update the status
    """

    @property
    def next_step(self):
        """
        This should be an enum from DepositorSteps
        """
        return NotImplementedError


class ReleaseView(viewsets.ViewSet):

    statistics = ReleaseSerializer()
    analysis_plan = AnalysisPlanSerializer()

    def create(self, request, *args, **kwargs):
        """
        """
        analysis_plan_id = request.data.get('analysis_plan_id')
        dp_statistics = request.data.get('dp_statistics')
        analysis_plan = get_object_or_error_response(AnalysisPlan, object_id=analysis_plan_id)
        release_info_serializer = ReleaseInfoSerializer()
        release_info_serializer.dp_statistics = dp_statistics
        if not release_info_serializer.is_valid():
            raise Exception("Invalid DPStatistics objects")

        stats_valid = release_info_serializer.save()
        return JsonResponse({'valid': stats_valid})

