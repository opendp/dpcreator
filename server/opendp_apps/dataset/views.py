from rest_framework import permissions, status
from rest_framework.response import Response

from opendp_apps.dataset.models import DataverseFileInfo, DataSetInfo
from opendp_apps.dataset.serializers import DataverseFileInfoSerializer, \
    DataSetInfoPolymorphicSerializer
from opendp_project.views import BaseModelViewSet


class DataSetInfoViewSet(BaseModelViewSet):
    queryset = DataSetInfo.objects.all().order_by('-created')
    serializer_class = DataSetInfoPolymorphicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This restricts the view to show only the DatasetInfo for the OpenDPUser
        """
        return self.queryset.filter(creator=self.request.user)


class DepositorSetupViewSet(BaseModelViewSet):
    queryset = DataverseFileInfo.objects.all()
    serializer_class = DataverseFileInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def partial_update(self, request, *args, **kwargs):
        acceptable_fields = ['user_step', 'dataset_questions', 'variable_ranges', 'variable_categories']
        problem_fields = []
        for field in request.data.keys():
            if field not in acceptable_fields:
                problem_fields.append(field)
        if problem_fields:
            return Response({'message': 'These fields are not updatable', 'fields': problem_fields},
                            status=status.HTTP_400_BAD_REQUEST)
        return super(DepositorSetupViewSet, self).partial_update(request, *args, **kwargs)