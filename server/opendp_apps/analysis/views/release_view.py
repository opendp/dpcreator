from rest_framework import permissions, viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from opendp_apps.utils.view_helper import get_json_error, get_json_success

from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis.validate_release_util import ValidateReleaseUtil
from opendp_apps.analysis.serializers import AnalysisPlanObjectIdSerializer, AnalysisPlanSerializer, \
    ReleaseValidationSerializer, ReleaseInfoSerializer


class ReleaseView(viewsets.ViewSet):

    analysis_plan = AnalysisPlanSerializer()
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['post', 'get']    # 'patch']

    def get_queryset(self):
        """
        AnalysisPlans for the currently authenticated user.
        """
        return AnalysisPlan.objects.filter(analyst=self.request.user)

    def retrieve(self, request, pk=None):
        release_info = get_object_or_404(ReleaseInfo, object_id=pk)
        serializer = ReleaseValidationSerializer(release_info)
        return Response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Override create to create a release based on a saved/pre-validated AnalysisPlan.dp_statistics

        endpoint: /api/release/

        Example POST input: `{"analysis_plan_id": "616b5167-4ce8-4def-85dc-6f0d8de2316c"}`

       -- Example outputs --

        (1) Overall error
            Status code: 400
                {
                    "success": false,
                    "message": "The statistic 'EyeHeight' had error xyz!"
                }

        (2) Release success
            Status code: 201
            {
                    "success": true,
                    "message": "release worked!",
                    "data":
                       (see: opendp_apps.release_info_formatter.get_release_data())

        """
        # Get the AnalysisPlan object_id
        #   - Bit redundant in the serializer re: retrieving plan but only using object_id--but okay!
        #     - e.g. Passing along the object_id only will lead to later running chain
        #       in a separate process and responding by websocket/lambda, etc.
        #
        serializer = AnalysisPlanObjectIdSerializer(data=request.data)
        if not serializer.is_valid():
            print(serializer.errors)
            if 'object_id' in serializer.errors:
                user_msg = '"object_id" error: %s' % (serializer.errors['object_id'][0])
            else:
                user_msg = 'Not a valid AnalysisPlan "object_id"'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # We have a good object_id!
        #
        analysis_plan_id = serializer.get_object_id()

        validate_util = ValidateReleaseUtil.compute_mode(request.user, analysis_plan_id)
        if validate_util.has_error():
            # This is a big error, check for it before evaluating individual statistics
            #
            user_msg = validate_util.get_err_msg()

            # Can you return a 400 / raise an Exception here with the error message?
            # How should this be used?
            return Response(get_json_error(user_msg), status=status.HTTP_400_BAD_REQUEST)

        # It worked! Return the release!
        release_info_obj = validate_util.get_new_release_info_object()
        serializer = ReleaseInfoSerializer(release_info_obj)
        return Response(data=serializer.data,
                        status=status.HTTP_201_CREATED)
