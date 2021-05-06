from rest_framework import permissions, viewsets

from opendp_apps.dataset.models import DataverseFileInfo, DataSetInfo
from opendp_apps.dataset.serializers import DataverseFileInfoSerializer, \
    DataSetInfoPolymorphicSerializer


class DataSetInfoViewSet(viewsets.ModelViewSet):
    queryset = DataSetInfo.objects.all().order_by('-created')
    serializer_class = DataSetInfoPolymorphicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This restricts the view to show only the DatasetInfo for the OpenDPUser
        """
        return self.queryset.filter(creator=self.request.user)


class DepositorSetup(viewsets.ModelViewSet):
    queryset = DataverseFileInfo.objects.all()
    serializer_class = DataverseFileInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
