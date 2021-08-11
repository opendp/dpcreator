from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import viewsets

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.dataverses.serializers import RegisteredDataverseSerializer
from opendp_apps.utils.view_helper import get_object_or_error_response
#from opendp_project.views import BaseModelViewSet

class RegisteredDataverseView(viewsets.ModelViewSet):
    """Publicly available listing of registered Dataverses"""

    queryset = RegisteredDataverse.objects.filter(active=True)
    #serializer_class = RegisteredDataverseSerializer
    http_method_names = ['get',]

    def list(self, request, *args, **kwargs):
        """Retrieve all active RegisteredDataverse objects"""
        serializer = RegisteredDataverseSerializer(self.queryset, many=True)

        return Response(data={'success': True,
                              'count': len(serializer.data),
                              'data': serializer.data},
                        status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Retrieve one RegisteredDataverse"""
        registered_dv = get_object_or_error_response(RegisteredDataverse, object_id=pk)
        serializer = RegisteredDataverseSerializer(registered_dv)

        return Response(data={'success': True,
                              'data': serializer.data},
                        status=status.HTTP_200_OK)
