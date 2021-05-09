from rest_framework import viewsets, status
from rest_framework.response import Response

from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses.dataverse_client import DataverseClient
from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataverses.serializers import DataverseFileInfoSerializer
from opendp_apps.user.models import DataverseUser
from opendp_apps.utils.view_helper import get_object_or_error_response


class DataverseFileView(viewsets.ViewSet):

    def get_serializer(self, instance=None):
        return DataverseFileInfoSerializer(context={'request': instance})

    def list(self, request):
        # TODO: This is to prevent errors in testing, why is test sending "AnonymousUser" in request?
        if not request.user.id:
            queryset = DataverseFileInfo.objects.all()
        else:
            queryset = DataverseFileInfo.objects.filter(creator=request.user)
        serializer = DataverseFileInfoSerializer(queryset, many=True)
        return Response(data={'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Get a Dataverse File corresponding to a user_id (UUID)
        and values from a DataverseHandoff object
        """
        # TODO: changing user_id to creator to match DB, we should standardize this naming convention
        handoff_id = request.data.get('handoff_id')
        user_id = request.data.get('creator')

        handoff = get_object_or_error_response(DataverseHandoff, object_id=handoff_id)
        dataverse_user = get_object_or_error_response(DataverseUser, object_id=user_id)

        try:
            file_info = DataverseFileInfo.objects.get(dataverse_file_id=handoff.fileId,
                                                      dv_installation=dataverse_user.dv_installation)
        except DataverseFileInfo.DoesNotExist:
            file_info = DataverseFileInfo(dv_installation=dataverse_user.dv_installation,
                                          dataverse_file_id=handoff.fileId,
                                          dataset_doi=handoff.datasetPid,
                                          file_doi=handoff.filePid,
                                          dataset_schema_info=None,
                                          file_schema_info=None,
                                          creator=dataverse_user.user)

        # If file info doesn't exist, call to Dataverse to get the data and
        # populate the relevant fields
        if not (file_info.dataset_schema_info or file_info.file_schema_info):
            params = file_info.as_dict()
            site_url = handoff.dv_installation.dataverse_url
            params[dv_static.DV_PARAM_SITE_URL] = site_url
            if not site_url:
                # shouldn't happen....
                return Response({'success': False, 'message': 'The Dataverse url has not been set.'},
                                status=status.HTTP_400_BAD_REQUEST)

            # (1) Retrieve the JSON LD info
            client = DataverseClient(site_url, handoff.apiGeneralToken)
            schema_org_resp = client.get_schema_org(handoff.datasetPid)
            if schema_org_resp.status_code >= 400:
                return Response({'success': False, 'message': schema_org_resp.message},
                                status=status.HTTP_400_BAD_REQUEST)


            # (2) Retrieve the file specific info from the JSON-LD
            #
            schema_org_content = schema_org_resp.json()
            file_schema_resp = DataverseManifestParams.get_file_specific_schema_info(schema_org_content,
                                                                                     handoff.fileId,
                                                                                     handoff.filePid)
            if not file_schema_resp.success:
                return Response({'success': False, 'message': file_schema_resp.message},
                                status=status.HTTP_400_BAD_REQUEST)

            # Update the DataverseFileInfo object
            #
            file_info.dataset_schema_info = schema_org_content
            file_info.file_schema_info = file_schema_resp.data
            # This will fail if the dataset_schema_info is malformed, use DOI as backup just in case:
            file_info.name = file_info.dataset_schema_info.get('name', file_info.dataset_doi)

            # Save the DataverseFileInfo updates
            file_info.save()

        serializer = DataverseFileInfoSerializer(file_info, context={'request': request})
        return Response({'success': True, 'data': serializer.data},
                        status=status.HTTP_201_CREATED)
