from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework import permissions, status
from rest_framework import serializers
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.utils.view_helper import get_json_error, get_json_success
from opendp_apps.model_helpers.basic_response import BasicResponse, ok_resp, err_resp


class DatasetObjectIdSerializer(serializers.Serializer):
    """Ensure input is a valid UUID and connected to a valid DataSetInfo object"""
    object_id = serializers.UUIDField()

    def validate_object_id(self, value):
        """
        Check that the blog post is about Django.
        """
        try:
            dsi = DataSetInfo.objects.get(object_id=value)
            self.dataset_info = dsi
        except DataSetInfo.DoesNotExist:
            raise serializers.ValidationError("DataSetInfo object not found")

        return value

    def get_dataset_info(self) -> BasicResponse:
        """Get the related DataSetInfo object"""
        assert self.is_valid(), "Do not call this method before checking \".is_valid()\""

        try:
            dsi = DataSetInfo.objects.get(object_id=self.validated_data.get('object_id'))
        except DataSetInfo.DoesNotExist:
            return err_resp("DataSetInfo object not found")

        return ok_resp(dsi)

    def get_dataset_info_with_user_check(self, user: get_user_model()) -> BasicResponse:
        """Get the related DataSetInfo object and check that the user matches the creator"""
        assert self.is_valid(), "Do not call this method before checking \".is_valid()\""

        try:
            dsi = DataSetInfo.objects.get(object_id=self.validated_data.get('object_id'),
                                          creator=user)
        except DataSetInfo.DoesNotExist:
            return err_resp("DataSetInfo object not found for current user.")

        return ok_resp(dsi)



class ProfilingViewSet(viewsets.ViewSet):
    """
    A viewset that provides custom profiling actions
    """
    serializer_class = DatasetObjectIdSerializer
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        return Response(get_json_success('ProfilingViewSet: custom actions only. In API docs, see "Extra Actions"'))

    @csrf_exempt
    @action(methods=['post'], detail=False, url_path='retrieve-profile')
    def retrieve_profile(self, request, *args, **kwargs):
        """Retrieve the DataSetInfo.profile_variables in JSON format.
        - Input: DataSetInfo.object_id (UUID in string format)
        \t\t- NOTE: The logged in user must match the DataSetInfo.creator
        - Output: DataSetInfo.profile_variables in JSON format
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
        resp_data = dict(object_id=dsi_object.object_id,
                         profile_variables=dsi_object.profile_variables)
        return Response(get_json_success('Profile found', data=resp_data))



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