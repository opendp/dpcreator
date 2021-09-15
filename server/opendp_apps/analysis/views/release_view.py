from rest_framework import viewsets, status
from rest_framework.response import Response

from opendp_apps.analysis.serializers import ComputationChainSerializer


class ReleaseView(viewsets.ViewSet):

    def create(self, request):
        computation_chain_serializer = ComputationChainSerializer(data=request.data)
        if not computation_chain_serializer.is_valid():
            raise Exception(f"Invalid Computation Chain request: {computation_chain_serializer.errors}")
        results = computation_chain_serializer.run_computation_chain()
        return Response({'results': results}, status=status.HTTP_201_CREATED)