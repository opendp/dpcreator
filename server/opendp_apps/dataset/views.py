from rest_framework import permissions, viewsets, serializers


from opendp_apps.dataset.models import DataverseFileInfo, DataSetInfo
from opendp_apps.dataset.serializers import DataSetInfoSerializer


class DataSetInfoViewSet(viewsets.ModelViewSet):
    queryset = DataSetInfo.objects.all().order_by('-created')
    serializer_class = DataSetInfoSerializer
    permission_classes = [permissions.IsAuthenticated]


class DataverseFileInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DataverseFileInfo
        fields = ['creator', 'installation_name', 'dataverse_file_id', 'dataset_doi', 'file_doi']


class DepositorSetup(viewsets.ModelViewSet):
    queryset = DataverseFileInfo.objects.all()
    serializer_class = DataverseFileInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # authentication_classes = [authentication.TokenAuthentication]
