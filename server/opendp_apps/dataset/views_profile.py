from collections import OrderedDict
from django.views.decorators.csrf import csrf_exempt

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import permissions, status
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from opendp_apps.async_messages.utils import get_websocket_id
from opendp_apps.dataset.serializers import DatasetObjectIdSerializer
from opendp_apps.utils.view_helper import get_json_error, get_json_success
from opendp_apps.async_messages.tasks import profile_dataset_info

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

        return Response(get_json_success())


    @csrf_exempt
    @action(methods=['post'], detail=False, url_path='retrieve-profile')
    def retrieve_profile(self, request, *args, **kwargs):
        """Retrieve the DataSetInfo.profile_variables in JSON format.
        - Input: DataSetInfo.object_id (UUID in string format)
        - Output: DataSetInfo.profile_variables in JSON format
        NOTES:
        - The logged in user must match the DataSetInfo.creator
        """
        print('\n>>request', request)
        print('\n>>request.data', request.data, type(request.data))

        # Is this a object_id a valid UUID?
        #
        ois = DatasetObjectIdSerializer(data=request.data)
        if not ois.is_valid():
            print(ois.errors)
            if 'object_id' in ois.errors:
                user_msg = '"object_id" error: %s' % (ois.errors['object_id'][0])
            else:
                user_msg = 'Not a valid "object_id"'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # Is there a related DataSetInfo where the logged in user is the
        #   DataSetInfo creator?
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


    #@csrf_exempt
    @action(methods=['post'], detail=False, url_path='run-async-profile')
    def run_async_profile(self, request, *args, **kwargs):
        """Asynchronously profile a DataSetInfo object, returning the DataSetInfo.profile_variables in JSON format.
        - Input: DataSetInfo.object_id (UUID in string format)
        - Output: DataSetInfo.profile_variables in JSON format
        NOTES:
        - The logged in user must match the DataSetInfo.creator
        - The response is returned asynchronously, via a websocket
        - If the profile already exists, it will be returned asynchronously.
        - If the DataSetInfo object is a DataverseFileInfo object, if necessary, this endpoint will both download the dataset in order to profile it.
        """
        # Is this a object_id a valid UUID?
        #
        ois = DatasetObjectIdSerializer(data=request.data)
        if not ois.is_valid():
            print(ois.errors)
            if 'object_id' in ois.errors:
                user_msg = '"object_id" error: %s' % (ois.errors['object_id'][0])
            else:
                user_msg = 'Not a valid "object_id"'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # Is there a related DataSetInfo where the logged in user is the
        #   DataSetInfo creator?
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



    #@csrf_exempt
    @action(methods=['post'], detail=False, url_path='run-direct-profile')
    def run_direct_profile(self, request, *args, **kwargs):
        """TEST ONLY - Profile a DataSetInfo object, returning the DataSetInfo.profile_variables in JSON format.
        - Input: DataSetInfo.object_id (UUID in string format)
        - Output: DataSetInfo.profile_variables in JSON format
        NOTES:
        - TEST ONLY: Uses the main web server thread
        - The logged in user must match the DataSetInfo.creator
        - The response is returned asynchronously, via a websocket
        - If the profile already exists, it will be returned asynchronously.
        - If the DataSetInfo object is a DataverseFileInfo object, if necessary, this endpoint will both download the dataset in order to profile it.
        """
        # Is this a object_id a valid UUID?
        #
        ois = DatasetObjectIdSerializer(data=request.data)
        if not ois.is_valid():
            #print(ois.errors)
            if 'object_id' in ois.errors:
                user_msg = '"object_id" error: %s' % (ois.errors['object_id'][0])
            else:
                user_msg = 'Not a valid "object_id"'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # Is there a related DataSetInfo where the logged in user is the
        #   DataSetInfo creator?
        #
        dsi_info = ois.get_dataset_info_with_user_check(request.user)
        if not dsi_info.success:
            return Response(get_json_error(dsi_info.message),
                            status=status.HTTP_404_NOT_FOUND)

        websocket_id = get_websocket_id(request)

        ddi_info = profile_dataset_info(ois.get_object_id(), websocket_id=websocket_id)
        if not ddi_info.success:
            return Response(get_json_error(ddi_info.message))

        dp_util = ddi_info.data

        user_msg = ('Profiling complete.')
        return Response(get_json_success(user_msg,
                                         data=dp_util.get_profile_variables()))

    #instance = self.get_object()
    #serializer_obj = self.get_serializer(instance=instance)
    #return Response(serializer_obj.data)
    # 5ce0e9a55ffa654bcee01238041fb31a


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