import logging

from django.conf import settings
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.response import Response

from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.dataset.models import DepositorSetupInfo, DatasetInfo, UploadFileInfo
from opendp_apps.dataset.permissions import IsOwnerOrBlocked
from opendp_apps.dataset.serializers import \
    (DatasetInfoPolymorphicSerializer,
     DepositorSetupInfoSerializer,
     UploadFileInfoSerializer,
     UploadFileInfoCreationSerializer)
from opendp_apps.utils.view_helper import get_json_error
from opendp_project.views import BaseModelViewSet

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DatasetInfoViewSet(BaseModelViewSet):
    """This class may be used for retrieving and updating DepositorSetupInfo, but NOT creating it"""
    queryset = DatasetInfo.objects.all().order_by('-created')
    serializer_class = DatasetInfoPolymorphicSerializer
    permission_classes = [permissions.IsAuthenticated]

    http_method_names = ['get', 'delete', 'patch']

    def get_queryset(self):
        """
        This restricts the view to show only the DatasetInfo for the OpenDPUser
        """
        logger.info(f"Getting DatasetInfo for user {self.request.user.object_id}")
        return self.queryset.filter(creator=self.request.user)


    def delete(self, request, *args, **kwargs):
        # We currently have on_delete set to protect, so we need to explicitly delete
        # the AnalysisPlan and ReleaseInfo objects first.
        release_info = ReleaseInfo.objects.filter(dataset=self.get_object())
        if release_info.exists():
            if not settings.ALLOW_RELEASE_DELETION:
                return Response(data=get_json_error('Deleting ReleaseInfo objects is not allowed'),
                                status=status.HTTP_401_UNAUTHORIZED)
            release_info.dataset = None
            release_info.save()
            release_info.delete()
        analysis_plans = AnalysisPlan.objects.filter(dataset=self.get_object()).update(dataset=None)
        analysis_plans.delete()
        return super().destroy(request, *args, **kwargs)


class DepositorSetupViewSet(BaseModelViewSet):
    queryset = DepositorSetupInfo.objects.all()
    serializer_class = DepositorSetupInfoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrBlocked]

    http_method_names = ['get', 'patch']

    def get_queryset(self):
        """
        This restricts the queryset to the DepositorSetupInfo objects where the
            creator is the logged in user
        """
        logger.info(f"Getting DepositorSetupInfo for user {self.request.user.object_id}")
        return self.queryset.select_related('creator').filter(creator=self.request.user)

    @transaction.atomic()
    def partial_update(self, request, *args, **kwargs):
        """
        Update DepositorSetupInfo fields
        """
        acceptable_fields = ['dataset_questions',
                             'epsilon_questions',
                             # 'user_step', # TODO: Remove this
                             'variable_info',
                             'epsilon',
                             'delta',
                             # 'default_epsilon', # TODO: Remove this
                             # 'default_delta', # TODO: Remove this
                             'confidence_level',
                             'wizard_step']

        # Adding fields_to_strip for MVP, simplify frontend changes which will be change in Sept
        fields_to_remove = ['user_step', 'default_epsilon', 'default_delta']
        for field_to_remove in fields_to_remove:
            request.data.pop(field_to_remove, None)

        problem_fields = []
        for field in request.data.keys():
            if field not in acceptable_fields:
                logger.info('not acceptable')
                problem_fields.append(field)

        if len(problem_fields) > 0:
            logger.error(f"Failed to update DepositorSetupInfo with fields {problem_fields}")
            return Response({'message': 'These fields are not updatable',
                             'fields': problem_fields},
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

from rest_framework import mixins

#class UploadFileSetupViewSet(mixins.CreateModelMixin): #BaseModelViewSet):
class UploadFileSetupViewSet(BaseModelViewSet):

    """Used only for creating an initial UploadFile"""
    serializer_class = UploadFileInfoCreationSerializer
    permission_classes = [IsOwnerOrBlocked]

    http_method_names = ['post', 'delete']

    @csrf_exempt
    def create(self, request, *args, **kwargs):
        """Create an UploadFileInfo object with default values"""
        info = super().create(request, *args, **kwargs)
        if info.status_code == status.HTTP_201_CREATED:
            new_object = UploadFileInfo.objects.get(object_id=info.data['object_id'])
            serializer = UploadFileInfoSerializer(new_object)  # serialize the data
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return info

    def get_queryset(self):
        """
        This restricts the queryset to the DepositorSetupInfo objects where the
            creator is the logged in user
        """
        logger.info(f"Getting UploadFileInfo for user {self.request.user.object_id}")
        return UploadFileInfo.objects.filter(creator=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Get the UploadFileInfo for the logged in user"""
        info = super().retrieve(request, *args, **kwargs)
        if info.status_code == status.HTTP_200_OK:
            upload_info = UploadFileInfo.objects.get(object_id=info.data['object_id'])
            serializer = UploadFileInfoSerializer(upload_info)  # serialize the data
            return Response(serializer.data, status=status.HTTP_200_OK)
        return info

    def list(self, request, *args, **kwargs):
        """
        List the UploadFileInfo for the logged in user
        Note: this is a minimal listing for debugging.
            See "UploadFileInfoSerializer" in opendp_apps/dataset/serializers for full output
        """
        # serializer = UploadFileInfoCreationSerializer(self.get_queryset(), many=True)
        serializer = UploadFileInfoSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)
