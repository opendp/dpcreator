from django.views.decorators.csrf import csrf_exempt

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.decorators import action

from opendp_project.views import BaseModelViewSet
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.serializers import AnalysisPlanSerializer
from opendp_apps.dataset.serializers import DatasetObjectIdSerializer
from opendp_apps.utils.view_helper import get_object_or_error_response

from opendp_apps.utils.view_helper import get_json_error, get_json_success


class AnalysisPlanViewSet(BaseModelViewSet): #viewsets.ModelViewSet):
    """Publicly available listing of registered Dataverses"""
    #serializer_class = AnalysisPlanSerializer
    serializer_classes = {
        'list': AnalysisPlanSerializer,
        'retrieve': AnalysisPlanSerializer,
        'create': DatasetObjectIdSerializer,
        #'create_default': DatasetObjectIdSerializer
        # ... other actions
    }
    default_serializer_class = AnalysisPlanSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


    #queryset = AnalysisPlan.objects.filter(active=True)
    http_method_names = ['get', 'post']

    def list(self, request, *args, **kwargs):
        """Purposely not implemented"""
        return Response(get_json_error("List via GET not available via API"),
                        status=status.HTTP_501_NOT_IMPLEMENTED)


    #def retrieve_unfinished_plan(self, request, ):
    #    """Retrieve an AnalysisPlan that is not yet complete--e.g. doesn't have a Release"""
    #    plans = AnalysisPlan.objects.filter(analyst=request.user)


    def retrieve(self, request, pk=None):
        """Retrieve one AnalysisPlan"""
        analysis_plan = get_object_or_error_response(AnalysisPlan,
                                                     object_id=pk,
                                                     analyst=request.user)
        serializer = AnalysisPlanSerializer(analysis_plan)

        return Response(get_json_success('AnalysisPlan retrieved', data=serializer.data),
                        status=status.HTTP_200_OK)


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
            return Response(get_json_success('AnalysisPlan created!', data=serializer.data),
                            status=status.HTTP_201_CREATED)

        # Nope! Error encountered!
        return Response(get_json_error(plan_util.message),
                        status=plan_util.data)
