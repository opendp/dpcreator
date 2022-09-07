import logging

from django.conf import settings
from rest_framework import permissions, viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from opendp_apps.analysis.serializers import \
    (IntegerEdgeInputsSerializer)
from opendp_apps.analysis.tools.bin_edge_helper import BinEdgeHelper
from opendp_apps.utils.view_helper import get_json_error

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class StatHelperView(viewsets.ViewSet):
    """
    Download **PUBLIC** JSON and PDF Release Files
    - View ONLY used for PUBLIC files
    """
    edge_inputs = IntegerEdgeInputsSerializer()
    permission_classes = [permissions.IsAuthenticated]

    # serializer_class = IntegerEdgeInputsSerializer
    # queryset = ReleaseInfo.objects.all()
    # permission_classes = [permissions.IsAuthenticated]
    # http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        """
        Not Allowed (or implemented).
        Hack to have the viewset be added to the router.
        """
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['POST'], url_path='make-edges-integer')
    def make_edges_integer(self, request):
        """
        Given a min, max, and # of bins, construct a list of edges.
        Example input: {"min": 1, "max": 100, "number_of_bins": 5}
        """

        serializer = IntegerEdgeInputsSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(get_json_error('Invalid input', errors=serializer.errors),
                            status=status.HTTP_400_BAD_REQUEST)

        beh = BinEdgeHelper(serializer.data['min'],
                            serializer.data['max'],
                            serializer.data['number_of_bins'])

        if beh.has_error():
            return Response(dict(message=get_json_error(beh.get_err_msg())),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "We have data!",
                         "data": beh.as_json()})
