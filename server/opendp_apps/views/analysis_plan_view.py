from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import viewsets

from opendp_project.views import BaseModelViewSet
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.analysis.models import AnalaysisPlan
from opendp_apps.analysis.analysis_plan_view import AnalysisPlanUtil
from opendp_apps.analysis.serializers import AnalaysisPlanSerializer
from opendp_apps.utils.view_helper import get_object_or_error_response

from opendp_apps.utils.view_helper import get_json_error, get_json_success


class AnalysisPlanView(BaseModelViewSet): #viewsets.ModelViewSet):
    """Publicly available listing of registered Dataverses"""

    queryset = AnalysisPlan.objects.filter(active=True)

    http_method_names = ['get', 'post']

    def list(self, request, *args, **kwargs):
        """Purposely not implemented"""
        return Response(get_json_error("Purposely not implemented"),
                        status=status.HTTP_501_NOT_IMPLEMENTED)


    def retrieve(self, request, pk=None):
        """Retrieve one AnalysisPlan"""
        analysis_plan = get_object_or_error_response(AnalysisPlan,
                                                     object_id=pk,
                                                     analyst=request.user)
        serializer = AnalaysisPlanSerializer(analysis_plan)

        return Response(get_json_success('AnalysisPlan retrieved', data=serializer.data),
                        status=status.HTTP_200_OK)


    def create(self, request, *args, **kwargs):
        """
        Create an AnalysisPlan object with default values
        """
        user = request.user
        dataset_object_id = request.data.get('object_id')

        # Use the AnalysisPlanUtil to create an AnalysisPlan
        #   with default values
        #
        plan_util = AnalysisPlanUtil.create_plan(dataset_object_id, user)

        # Did AnalysisPlan creation work?
        if plan_util.success:
            # Yes, it worked!
            new_plan = plan_util.data                       # "data" holds the AnalysisPlan object
            serializer = AnalaysisPlanSerializer(new_plan)  # serialize the data

            # Return it
            return Response(get_json_success('AnalysisPlan created!', data=serializer.data),
                            status=status.HTTP_201_CREATED)

        # Nope! Error encountered!
        return Response(get_json_error(plan_util.message),
                        status=plan_util.data)
