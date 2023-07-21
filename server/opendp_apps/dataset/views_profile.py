import logging

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions
from rest_framework import status, viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.decorators import action
from rest_framework.response import Response

from opendp_apps.async_messages.tasks import profile_dataset_info
from opendp_apps.async_messages.utils import get_websocket_id
from opendp_apps.dataset.serializers import DatasetObjectIdSerializer
from opendp_apps.dataverses.download_and_profile_util import DownloadAndProfileUtil
from opendp_apps.utils.view_helper import get_json_error, get_json_success

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class ProfilingViewSet(viewsets.ViewSet):
    """
    A viewset that provides custom profiling actions
    """
    serializer_class = DatasetObjectIdSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Only used so that these endpoints show up in the docs"""
        user_msg = ('ProfilingViewSet: custom actions only.'
                    ' In API docs, see "Extra Actions"')
        return Response(get_json_error(user_msg),
                        status=status.HTTP_501_NOT_IMPLEMENTED)

    @csrf_exempt
    @action(methods=['post'], detail=False, url_path='retrieve-profile')
    def retrieve_profile(self, request, *args, **kwargs):
        """Retrieve the DatasetInfo.profile_variables in JSON format.
        - Input: DatasetInfo.object_id (UUID in string format)
        - Output: DatasetInfo.profile_variables in JSON format
        NOTES:
        - The logged in user must match the DatasetInfo.creator
        """
        # Is this a object_id a valid UUID?
        #
        ois = DatasetObjectIdSerializer(data=request.data)
        if not ois.is_valid():
            logger.error(ois.errors)
            if 'object_id' in ois.errors:
                user_msg = '"object_id" error: %s' % (ois.errors['object_id'][0])
            else:
                user_msg = 'Not a valid "object_id"'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # Is there a related DatasetInfo where the logged in user is the
        #   DatasetInfo creator?
        #
        dsi_info = ois.get_dataset_info_with_user_check(request.user)
        if not dsi_info.success:
            return Response(get_json_error(dsi_info.message),
                            status=status.HTTP_404_NOT_FOUND)

        # Does the profile exist?
        #
        dsi_object = dsi_info.data
        if not dsi_object.profile_variables:
            user_msg = 'Dataset not profiled'
            # status for profile?
            return Response(get_json_error(user_msg))

        # Profile found!
        #
        return Response(get_json_success('Profile found', data=dsi_object.get_profile_variables()))

    @action(methods=['post'], detail=False, url_path='run-async-profile')
    def run_async_profile(self, request, *args, **kwargs):
        """Asynchronously profile a DatasetInfo object, returning the DatasetInfo.profile_variables in JSON format.
        - Input: DatasetInfo.object_id (UUID in string format)
        - Output: DatasetInfo.profile_variables in JSON format
        NOTES:
        - The logged in user must match the DatasetInfo.creator
        - The response is returned asynchronously, via a websocket
        - If the profile already exists, it will be returned asynchronously.
        - If the DatasetInfo object is a DataverseFileInfo object, if necessary, this endpoint will both download the dataset in order to profile it.
        """
        # Is this a object_id a valid UUID?
        #
        ois = DatasetObjectIdSerializer(data=request.data)
        if not ois.is_valid():
            logger.error(ois.errors)
            if 'object_id' in ois.errors:
                user_msg = '"object_id" error: %s' % (ois.errors['object_id'][0])
            else:
                user_msg = 'Not a valid "object_id"'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # Is there a related DatasetInfo where the logged in user is the
        #   DatasetInfo creator?
        #
        dsi_info = ois.get_dataset_info_with_user_check(request.user)
        if not dsi_info.success:
            return Response(get_json_error(dsi_info.message),
                            status=status.HTTP_404_NOT_FOUND)

        websocket_id = get_websocket_id(request)

        profile_dataset_info.delay(ois.get_object_id(), websocket_id=websocket_id)

        user_msg = ('Profiling process started. Responses will be sent via'
                    f' messages to websocket: {websocket_id}')
        return Response(get_json_success(user_msg))

    @action(methods=['post'], detail=False, url_path='run-direct-profile')
    def run_direct_profile(self, request, *args, **kwargs):
        """TEST ONLY - Profile a DatasetInfo object, returning the DatasetInfo.profile_variables in JSON format.
        - Input: DatasetInfo.object_id (UUID in string format)
        - Output: DatasetInfo.profile_variables in JSON format
        NOTES:
        - TEST ONLY: Uses the main web server thread
        - The logged in user must match the DatasetInfo.creator
        - The response is returned asynchronously, via a websocket
        - If the profile already exists, it will be returned asynchronously.
        - If the DatasetInfo object is a DataverseFileInfo object, if necessary, this endpoint will both download the dataset in order to profile it.
        """
        # Is this a object_id a valid UUID?
        #
        ois = DatasetObjectIdSerializer(data=request.data)
        if not ois.is_valid():
            logger.error(ois.errors)
            if 'object_id' in ois.errors:
                user_msg = '"object_id" error: %s' % (ois.errors['object_id'][0])
            else:
                user_msg = 'Not a valid "object_id"'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # Is there a related DatasetInfo where the logged in user is the
        #   DatasetInfo creator?
        #
        dsi_info = ois.get_dataset_info_with_user_check(request.user)
        if not dsi_info.success:
            return Response(get_json_error(dsi_info.message),
                            status=status.HTTP_404_NOT_FOUND)

        websocket_id = get_websocket_id(request)
        print('websocket_id', websocket_id)

        ddi_info = profile_dataset_info(ois.get_object_id(), websocket_id=websocket_id)
        if not ddi_info.success:
            return Response(get_json_error(ddi_info.message))

        dp_util = ddi_info.data

        user_msg = ('Profiling complete.')
        return Response(get_json_success(user_msg,
                                         data=dp_util.get_profile_variables()))

    @action(methods=['post'], detail=False, url_path='run-direct-profile-no-async')
    def run_direct_profile_no_async(self, request, *args, **kwargs):
        """Profile a DatasetInfo object
        - Input: DatasetInfo.object_id (UUID in string format)
        - Output: Data profile in JSON format
        NOTES:
        - TEST ONLY: Uses the main web server thread
        - The logged in user must match the DatasetInfo.creator
        - The response is returned **synchronously**
        - If the profile already exists, it will be returned asynchronously.
        - If the DatasetInfo object is a DataverseFileInfo object, if necessary, this endpoint will both download the dataset in order to profile it.
        """
        # Is this a object_id a valid UUID?
        #
        ois = DatasetObjectIdSerializer(data=request.data)
        if not ois.is_valid():
            logger.error(ois.errors)
            if 'object_id' in ois.errors:
                user_msg = '"object_id" error: %s' % (ois.errors['object_id'][0])
            else:
                user_msg = 'Not a valid "object_id"'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # Is there a related DatasetInfo where the logged in user is the
        #   DatasetInfo creator?
        #
        dsi_info = ois.get_dataset_info_with_user_check(request.user)
        if not dsi_info.success:
            return Response(get_json_error(dsi_info.message),
                            status=status.HTTP_404_NOT_FOUND)

        dp_util = DownloadAndProfileUtil(ois.get_object_id(), websocket_id=None)
        if dp_util.has_error():
            return Response(get_json_error(dp_util.get_err_msg()),
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(get_json_success('Profile Complete',
                                         data=dp_util.get_data_profile()),
                        status=status.HTTP_200_OK)


"""
curl http://127.0.0.1:8000/api/profile/retrieve-profile/

curl -u dev_admin:admin --header "Content-Type: application/json" \
  --request POST \
  --data '{"object_id":"xyz"}' \
  http://127.0.0.1:8000/api/profile/retrieve-profile/
  

curl -u dev_admin:admin --header "Content-Type: application/json" \
  --request POST \
  --data '{"object_id":"af0d01d4-073c-46fa-a2ff-829193828b82"}' \
  http://127.0.0.1:8000/api/profile/retrieve-profile/
  


data = dict(object_id='5ce0e9a55ffa654bcee01238041fb31a')
ois = ObjectIdSerializer(data=data)
ois.is_valid()
ois.validated_data
ois.validated_data.get('object_id')  
  
"""
