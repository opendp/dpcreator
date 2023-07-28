import logging

from django.conf import settings
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework import permissions, status
from rest_framework.response import Response

from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.dataset import static_vals as dstatic
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

        # -------------------------------------------------------
        # (1) Make sure the logged in user is the DepositorSetupInfo.creator!
        # -------------------------------------------------------
        depositor_setup_info = self.get_object()
        if request.user != depositor_setup_info.creator:
            return Response({'detail': 'Not found.'},
                            status=status.HTTP_404_NOT_FOUND)

        # -------------------------------------------------------
        # (2) Determine type of update -> which fields are updateable
        #   If the DepositorSetupInfo "is_complete", restrict updates
        # -------------------------------------------------------
        num_fields_to_update = len(request.data.keys())

        # Case A: "is_complete" has been set to True
        #   Only the "wizard_step" field may be updated
        #
        if depositor_setup_info.is_complete:
            if dstatic.KEY_WIZARD_STEP not in request.data:
                return Response(get_json_error(dstatic.ERR_MSG_ONLY_WIZARD_ALREADY_COMPLETE),
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                acceptable_fields = ['wizard_step']
        elif 'is_complete' in request.data:
            # Case B: Setting "is_complete"
            #   This is a special case, it means the user is indicating completion of the setup process.
            #   The only additional field that may be updated is "wizard_step"
            #
            if num_fields_to_update == 1 or \
                    (num_fields_to_update == 2 and dstatic.KEY_WIZARD_STEP in request.data):

                # Can only set is_complete when the other steps are complete
                #
                if depositor_setup_info.user_step != \
                        DepositorSetupInfo.DepositorSteps.STEP_0600_EPSILON_SET:
                    # Send  error message
                    user_msg = dstatic.ERR_MSG_COMPLETE_NOT_ALLOWED_INVALID_DATA
                    return Response(get_json_error(user_msg),
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    acceptable_fields = ['is_complete', 'wizard_step']
            else:
                key_list_str = ', '.join(list(request.data.keys()))
                user_msg = dstatic.ERR_MSG_ONLY_WIZARD_STEP_MAY_BE_UPDATED.format(key_list_str=key_list_str)
                return Response(get_json_error(user_msg),
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            # Case C: Setup is incomplete, allow updates of:
            #   wizard_step, dataset_questions, epsilon_questions,
            #   variable_info, epsilon, delta, confidence_level
            #
            acceptable_fields = ['wizard_step',
                                 'dataset_questions',
                                 'epsilon_questions',
                                 'variable_info',
                                 'epsilon',
                                 'delta',
                                 'confidence_level']

        # -------------------------------------------------------
        # TODO: Update frontend
        # This is an MVP "hack" to simplify frontend changes which will be changed in Sept
        # -------------------------------------------------------
        fields_to_remove = ['user_step', 'default_epsilon', 'default_delta']
        for field_to_remove in fields_to_remove:
            request.data.pop(field_to_remove, None)

        # -------------------------------------------------------
        # Use the "acceptable_fields" to make the update
        # -------------------------------------------------------
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

        return super(DepositorSetupViewSet, self).partial_update(request, *args, **kwargs)


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
