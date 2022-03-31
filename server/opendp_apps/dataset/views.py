import logging

from django.conf import settings
from django.db import transaction
from rest_framework import permissions, status
from rest_framework.response import Response

from opendp_apps.analysis.models import AnalysisPlan, DepositorSetupInfo
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.dataset.permissions import IsOwnerOrBlocked
from opendp_apps.dataset.serializers import DataSetInfoPolymorphicSerializer, DepositorSetupInfoSerializer
from opendp_project.views import BaseModelViewSet


logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DataSetInfoViewSet(BaseModelViewSet):
    queryset = DataSetInfo.objects.all().order_by('-created')
    serializer_class = DataSetInfoPolymorphicSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This restricts the view to show only the DatasetInfo for the OpenDPUser
        """
        logger.info(f"Getting DataSetInfo for user {self.request.user.object_id}")
        return self.queryset.filter(creator=self.request.user)


class DepositorSetupViewSet(BaseModelViewSet):
    queryset = DepositorSetupInfo.objects.all()
    serializer_class = DepositorSetupInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrBlocked]

    def get_queryset(self):
        """
        This restricts the queryset to the DepositorSetupInfo objects where the
            creator is the logged in user
        """
        logger.info(f"Getting DepositorSetupInfo for user {self.request.user.object_id}")
        return self.queryset.filter(creator=self.request.user)

    @transaction.atomic()
    def partial_update(self, request, *args, **kwargs):
        """
        Update DepositorSetupInfo fields
        """
        acceptable_fields = ['user_step',
                             'dataset_questions', 'epsilon_questions',
                             'variable_info',
                             'default_epsilon', 'epsilon',
                             'default_delta', 'delta',
                             'confidence_level']
        problem_fields = []
        for field in request.data.keys():
            if field not in acceptable_fields:
                problem_fields.append(field)
        if problem_fields:
            logger.error(f"Failed to update DepositorSetupInfo with fields {problem_fields}")
            return Response({'message': 'These fields are not updatable', 'fields': problem_fields},
                            status=status.HTTP_400_BAD_REQUEST)

        # -----------------------------------------------------------------
        # Allow a depositor to return to the "Confirm Variables" page
        #   and update min/max, categories, etc.
        #
        # Depositor workflow only, allow edits to DepositorSetupInfo.variable_info
        #   to also be sent to AnalysisPlan.variable_info, if an AnalysisPlan exists
        # TODO: Fix this for Analyst workflow
        # -----------------------------------------------------------------
        if 'variable_info' in request.data:
            # Get the DepositorSetupInfo
            setup_info = DepositorSetupInfo.objects.filter(object_id=kwargs.get('object_id')).first()
            if setup_info:
                # Does an AnalysisPlan exist?
                analysis_plan = AnalysisPlan.objects.filter(dataset=setup_info.get_dataset_info()).first()

                # Yes, if not submitted or complete, update it
                #
                if analysis_plan and analysis_plan.is_editable():
                    analysis_plan.variable_info = request.data['variable_info']
                    analysis_plan.save()
                    logger.info(f"DepositorSetupViewSet: AnalysisPlan updated with variable info "
                                f"{request.data['variable_info']}")

        return super(DepositorSetupViewSet, self).partial_update(request, *args, **kwargs)