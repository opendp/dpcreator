from rest_framework import viewsets
from rest_framework.response import Response

from opendp_apps.analysis.serializers import AnalysisPlanSerializer, \
    ReleaseInfoSerializer


class ReleaseView(viewsets.ViewSet):

    statistics = ReleaseInfoSerializer()
    analysis_plan = AnalysisPlanSerializer()

    def create(self, request, *args, **kwargs):
        """
        Run validation for a list of release requests
        """
        release_info_serializer = ReleaseInfoSerializer(data=request.data)
        if not release_info_serializer.is_valid():
            raise Exception("Invalid DPStatistics objects")
        stats_valid = release_info_serializer.save()
        return Response({'valid': stats_valid})

