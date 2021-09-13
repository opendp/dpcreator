from rest_framework import viewsets, status
from rest_framework.response import Response

from opendp_apps.analysis.serializers import AnalysisPlanSerializer, \
    ReleaseValidationSerializer, ComputationChainSerializer


class ReleaseView(viewsets.ViewSet):

    statistics = ReleaseValidationSerializer()
    analysis_plan = AnalysisPlanSerializer()

    def create(self, request, *args, **kwargs):
        """
        Run validation for a list of release requests
        """
        print('>> ReleaseView.create >>>', request.data)
        release_info_serializer = ReleaseValidationSerializer(data=request.data)
        if not release_info_serializer.is_valid():
            raise Exception(f"Invalid DPStatistics objects: {release_info_serializer.errors}")
        stats_valid = release_info_serializer.save()
        return Response({'valid': stats_valid}, status=status.HTTP_201_CREATED)

    def update(self, request, object_id=None):
        # TODO: This maybe should be under the POST method but with a flag (validation=false actually runs the chain)
        computation_chain_serializer = ComputationChainSerializer(data=request.data)
        if not computation_chain_serializer.is_valid():
            raise Exception(f"Invalid Computation Chain request: {computation_chain_serializer.errors}")
        results = computation_chain_serializer.run_computation_chain()
        return Response({'results': results}, status=status.HTTP_201_CREATED)