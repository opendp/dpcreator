from rest_framework import viewsets, status
from rest_framework.response import Response
from opendp_apps.utils.view_helper import get_json_error, get_json_success

from opendp_apps.analysis.serializers import AnalysisPlanSerializer, \
    ReleaseValidationSerializer, ComputationChainSerializer


class ReleaseView(viewsets.ViewSet):

    statistics = ReleaseValidationSerializer()
    analysis_plan = AnalysisPlanSerializer()

    http_method_names = ['get', 'post', 'patch']

    def create(self, request, object_id=None):
        # TODO: This maybe should be under the POST method but with a flag (validation=false actually runs the chain)
        computation_chain_serializer = ComputationChainSerializer(data=request.data)
        if not computation_chain_serializer.is_valid():
            raise Exception(f"Invalid Computation Chain request: {computation_chain_serializer.errors}")
        results = computation_chain_serializer.run_computation_chain()
        return Response({'results': results}, status=status.HTTP_201_CREATED)