from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import viewsets

from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.dataverses.serializers import RegisteredDataverseSerializer
from opendp_apps.utils.view_helper import get_object_or_error_response

from opendp_apps.utils.view_helper import get_json_error, get_json_success


class RegisteredDataverseView(viewsets.ModelViewSet):
    """Publicly available listing of registered Dataverses"""

    queryset = RegisteredDataverse.objects.filter(active=True)
    http_method_names = ['get',]

    def list(self, request, *args, **kwargs):
        """Retrieve all active RegisteredDataverse objects"""
        serializer = RegisteredDataverseSerializer(self.queryset, many=True)

        num_dvs = len(serializer.data)
        success = False
        message = "No registered Dataverses found."
        if num_dvs > 0:
            success = True
            message = f"{num_dvs} registered Dataverse(s) found."

        if success:
            return Response(get_json_success(message,
                                             data=dict(count=num_dvs, dataverses=serializer.data)),
                            status=status.HTTP_200_OK)

        return Response(get_json_error(message),
                        status=status.HTTP_404_NOT_FOUND)


    def retrieve(self, request, pk=None):
        """Retrieve one RegisteredDataverse"""
        registered_dv = get_object_or_error_response(RegisteredDataverse, object_id=pk)
        serializer = RegisteredDataverseSerializer(registered_dv)

        return Response(get_json_success('Dataverse retrieved', data=serializer.data),
                        status=status.HTTP_200_OK)
