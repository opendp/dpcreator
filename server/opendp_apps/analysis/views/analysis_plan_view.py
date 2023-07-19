import logging
from django.utils.timezone import make_aware
from datetime import datetime
from django.conf import settings
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.analysis_plan_creator import AnalysisPlanCreator
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis.serializers import \
    AnalysisPlanSerializer
from opendp_apps.dataset.serializers import DatasetObjectIdSerializer
from opendp_apps.utils.view_helper import get_json_error
from opendp_project.views import BaseModelViewSet

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class AnalysisPlanViewSet(BaseModelViewSet):
    """Publicly available listing of registered Dataverses"""
    serializer_classes = {
        'list': AnalysisPlanSerializer,
        'retrieve': AnalysisPlanSerializer,
        'create': DatasetObjectIdSerializer,
        'partial_update': AnalysisPlanSerializer,
        'destroy': AnalysisPlanSerializer
    }
    default_serializer_class = AnalysisPlanSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        """
        AnalysisPlans for the currently authenticated user.
        """
        logger.info(f"Getting AnalysisPlans for user {self.request.user.object_id}")
        return AnalysisPlan.objects.select_related('dataset'
                                                   ).filter(Q(analyst=self.request.user) |
                                                            Q(dataset__creator=self.request.user))

    @csrf_exempt
    def create(self, request, *args, **kwargs):
        """Create an AnalysisPlan object with default values"""

        # Is this object_id a valid UUID?
        #
        ois = DatasetObjectIdSerializer(data=request.data)
        if not ois.is_valid():
            if 'object_id' in ois.errors:
                user_msg = '"object_id" error: %s' % (ois.errors['object_id'][0])
            else:
                user_msg = 'Not a valid "object_id"'
            logger.error(user_msg + " " + ois.data['object_id'])
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # Is there a related DataSetInfo where the logged in user is the
        #   DataSetInfo creator?
        #
        dsi_info = ois.get_dataset_info_with_user_check(request.user)
        if not dsi_info.success:
            logger.error(dsi_info.message)
            return Response(get_json_error(dsi_info.message),
                            status=status.HTTP_404_NOT_FOUND)

        # Use the AnalysisPlanUtil to create an AnalysisPlan
        #   with default values
        #
        plan_creator = AnalysisPlanCreator(request.user,
                                           request.data)

        # Did AnalysisPlan creation work?
        if plan_creator.has_error():
            return Response(get_json_error(plan_creator.get_err_msg()),
                            status=status.HTTP_400_BAD_REQUEST)

        # Yes, it worked!
        serializer = AnalysisPlanSerializer(plan_creator.analysis_plan)  # serialize the data
        logger.info(f"AnalysisPlan created: {serializer.data}")

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """Allows the AnalysisPlan.analyst to make updates to the AnalysisPlan object."""

        # Make sure this is the AnalysisPlan.analyst!
        #   The AnalysisPlan.dataset.creator cannot make changes via API
        analysis_plan = self.get_object()
        if analysis_plan.analyst != request.user:
            return Response({'detail': 'Not found.'},
                            status=status.HTTP_404_NOT_FOUND)

        # Does the AnalysisPlan already have a release?
        if analysis_plan.release_info:
            return Response(get_json_error(astatic.ERR_MSG_RELEASES_EXISTS),
                            status=status.HTTP_400_BAD_REQUEST)

        # Is the AnalysisPlan expired?
        if make_aware(datetime.now()) > analysis_plan.expiration_date:
            return Response(get_json_error(astatic.ERR_MSG_ANALYSIS_PLAN_EXPIRED),
                            status=status.HTTP_400_BAD_REQUEST)

        # Check that only the allowed fields are being updated
        #
        acceptable_fields = ['name', 'description', 'variable_info', 'dp_statistics', 'wizard_step']
        problem_fields = []
        fields_to_update = []
        for field in request.data.keys():
            if field not in acceptable_fields:
                problem_fields.append(field)
            else:
                fields_to_update.append(field)

        # If there are any problem fields, return an error
        #
        if problem_fields:
            problem_field_str = ', '.join([str(f) for f in problem_fields])
            user_msg = astatic.ERR_MSG_FIELDS_NOT_UPDATEABLE.format(problem_field_str=problem_field_str)
            return Response(get_json_error(user_msg),
                            status=status.HTTP_400_BAD_REQUEST)

        # If there are no fields to update, return an error
        #
        if not fields_to_update:
            return Response(get_json_error(f'There are no fields to update'),
                            status=status.HTTP_400_BAD_REQUEST)

        # Make the partial update
        #
        partial_update_result = super(AnalysisPlanViewSet, self).partial_update(request, *args, **kwargs)
        # logger.info("Analysis update with request " + json.dumps(request.data))

        return partial_update_result

    def delete(self, request, *args, **kwargs):
        """
        Allow the Analyst or DataSetInfo.creator to delete an AnalysisPlan object.
        If an associated ReleaseInfo exists, delete is not allowed
        """
        analysis_plan = self.get_object()
        if analysis_plan.release_info.exists():
            if not settings.ALLOW_RELEASE_DELETION:
                return Response(get_json_error(('Deleting AnalysisPlan with an associated '
                                                'ReleaseInfo is not allowed')),
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                analysis_plan.release_info.delete()

        return super().destroy(request, *args, **kwargs)
