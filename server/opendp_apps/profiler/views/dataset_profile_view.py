"""Endpoint to profile dataset info"""
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler.tasks import run_profile_by_filefield

from opendp_apps.dataset.models import DataSetInfo


class DatasetProfileInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSetInfo
        fields = ['object_id']


class DatasetProfileView(viewsets.ViewSet):

    permission_classes = [permissions.IsAuthenticated]

    #serializer_class = DatasetProfileInfoSerializer
    def get_serializer(self, instance=None):
        return DatasetProfileInfoSerializer(context={'request': instance})

    def list(self, request):
        """Placeholder to allow documentation"""
        return Response({'success': True,
                         'message': '(only here to allow documentation)'},
                        status=status.HTTP_200_OK)


    @action(detail=False, methods=['post'])
    def profile_dataset(self, request):
        """API call to profile the dataset"""

        dataset_id = request.data.get('dataset_id')
        if not dataset_id:
            return Response({'success': False,
                             'message': 'dataset_id not set'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the DataSetInfo object
        try:
            dataset_info = DataSetInfo.objects.get(pk=dataset_id)
        except DataSetInfo.DoesNotExist:
            # Should this be a 400 or a 401, e.g. to protect from object discovery
            return Response({'success': False,
                             'message': 'DataSetInfo object not found'},
                            status=status.HTTP_404_NOT_FOUND)


        # Check user permissions (dataset_info needed to check permissions)
        #
        user = request.user()
        if user.is_superuser or (user == dataset_info.creator):
            pass # user has permissions
        else:
            return Response({'success': False,
                             'message': 'No permissions for this operation.'},
                            status=status.HTTP_401_UNAUTHORIZED)

        # Does a profile already exist?
        #
        if dataset_info.data_profile:
            # data profile exists
            return Response({'success': False,
                             'message': 'Dataset already has a profile.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Kick off the profiler, async process
        #
        params = {pstatic.KEY_WEBSOCKET_ID: user.object_id}
        run_profile_by_filefield.delay(dataset_info.object_id, **params)

        return Response({'success': True,
                         'message': 'Profiler started'},
                        status=status.HTTP_200_OK)

"""
from opendp_apps.profiler.views.dataset_profile_view import DatasetProfileView
v = DatasetProfileView(basename='profiler')
v.reverse_action(url_name='profile-dataset')
"""