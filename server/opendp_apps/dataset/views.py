from rest_framework import permissions, viewsets

from opendp_apps.dataset.models import DataverseFileInfo, DataSetInfo
from opendp_apps.dataset.serializers import DataSetInfoSerializer, DataverseFileInfoSerializer


class DataSetInfoViewSet(viewsets.ModelViewSet):
    queryset = DataSetInfo.objects.all().order_by('-created')
    serializer_class = DataSetInfoSerializer
    permission_classes = [permissions.IsAuthenticated]


class DepositorSetup(viewsets.ModelViewSet):
    queryset = DataverseFileInfo.objects.all()
    serializer_class = DataverseFileInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # authentication_classes = [authentication.TokenAuthentication]
