from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.response import Response

from opendp_project.views import BaseModelViewSet
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.serializers import \
    AnalysisPlanSerializer
from opendp_apps.dataset.serializers import DatasetObjectIdSerializer

from opendp_apps.utils.view_helper import get_json_error


class AnalysisPlanViewSet(BaseModelViewSet):
    """Publicly available listing of registered Dataverses"""
    serializer_classes = {
        'list': AnalysisPlanSerializer,
        'retrieve': AnalysisPlanSerializer,
        'create': DatasetObjectIdSerializer,
        'partial_update': AnalysisPlanSerializer,
    }
    default_serializer_class = AnalysisPlanSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    http_method_names = ['get', 'post', 'patch']

    def get_queryset(self):
        """
        AnalysisPlans for the currently authenticated user.
        """
        return AnalysisPlan.objects.filter(analyst=self.request.user)

    @csrf_exempt
    def create(self, request, *args, **kwargs):
        """
        Create an AnalysisPlan object with default values
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

        # Use the AnalysisPlanUtil to create an AnalysisPlan
        #   with default values
        #
        plan_util = AnalysisPlanUtil.create_plan(ois.get_object_id(), request.user)

        # Did AnalysisPlan creation work?
        if plan_util.success:
            # Yes, it worked!
            new_plan = plan_util.data                       # "data" holds the AnalysisPlan object
            serializer = AnalysisPlanSerializer(new_plan)  # serialize the data

            # Return it
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # Nope! Error encountered!
        return Response(get_json_error(plan_util.message),
                        status=plan_util.data)

    def partial_update(self, request, *args, **kwargs):
        """Make updates to the AnalysisPlan object"""
        print('>>> partial_update: ', request.data)
        acceptable_fields = ['variable_info', 'dp_statistics', 'user_step']
        problem_fields = []
        fields_to_update = []
        for field in request.data.keys():
            if field not in acceptable_fields:
                problem_fields.append(field)
            else:
                fields_to_update.append(field)
        if problem_fields:
            problem_field_list = ', '.join([str(f) for f in problem_fields])
            user_msg = f'{astatic.ERR_MSG_FIELDS_NOT_UPDATEABLE}: {problem_field_list}'
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        if not fields_to_update:
            return Response(get_json_error(f'There are no fields to update'),
                            status=status.HTTP_400_BAD_REQUEST)

        return super(AnalysisPlanViewSet, self).partial_update(request, *args, **kwargs)