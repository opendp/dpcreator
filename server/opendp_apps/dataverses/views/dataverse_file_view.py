from rest_framework import viewsets, status
from rest_framework.response import Response

from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses.dataverse_client import DataverseClient
from opendp_apps.dataverses.dataverse_request_handler import DataverseRequestHandler
from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.serializers import DataverseFileInfoSerializer
from opendp_apps.user.models import DataverseUser
from opendp_apps.utils.view_helper import get_object_or_error_response


class DataverseFileView(viewsets.ViewSet):

    def list(self, request):
        handoff_id = request.query_params.get('handoff_id')
        user_id = request.query_params.get('user_id')
        dataverse_user = get_object_or_error_response(DataverseUser, object_id=user_id)
        opendp_user = dataverse_user.user
        registered_dataverse = dataverse_user.dv_installation
        handoff = get_object_or_error_response(DataverseHandoff, object_id=handoff_id)

        try:
            file_info = DataverseFileInfo.objects.get(dataverse_file_id=handoff.fileId,
                                                      dv_installation=registered_dataverse)
        except DataverseFileInfo.DoesNotExist:
            file_info = DataverseFileInfo(dv_installation=registered_dataverse,
                                          # TODO: Should this be a UUID as well?
                                          dataverse_file_id=1,
                                          dataset_doi=handoff.datasetPid,
                                          file_doi=handoff.filePid,
                                          dataset_schema_info=None,
                                          file_schema_info=None,
                                          creator=opendp_user)

        if not (file_info.dataset_schema_info or file_info.file_schema_info):
            params = file_info.as_dict()
            params['siteUrl'] = handoff.siteUrl
            client = DataverseClient(handoff.siteUrl, handoff.apiGeneralToken)
            schema_org_content = client.get_schema_org(handoff.datasetPid)
            request_handler = DataverseRequestHandler(params, opendp_user)
            schema_info = request_handler.mparams.get_schema_org()
            # print(schema_info.json())
            if schema_info.status_code >= 400:
                # print(schema_info.message)
                request_handler.add_err_msg(schema_info.message)
            file_schema_info = request_handler.mparams.get_file_specific_schema_info(schema_info.json())
            # print(schema_info.as_dict(), file_schema_info.as_dict())
            file_info.dataset_schema_info = schema_org_content.json()
            file_info.file_schema_info = file_schema_info.as_dict()
        file_info.save()
        # print(file_info)
        serializer = DataverseFileInfoSerializer(file_info, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)
