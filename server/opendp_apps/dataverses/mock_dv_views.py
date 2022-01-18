"""
Views meant to mimic calls by PyDataverse
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings

from django.http import HttpResponse, JsonResponse
from opendp_apps.dataverses.models import ManifestTestParams
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataverses.dataverse_request_handler import DataverseRequestHandler
from opendp_apps.dataverses import static_vals as dv_static


@login_required
def view_dataverse_incoming_1(request):
    """Do something with incoming DV info ..."""

    resp_info = dict(title='Process Incoming Params',
                     subtitle='Example 1: get user info, schema',
                     incoming_params=[(k, v) for k, v in request.GET.items()])

    mparams = DataverseManifestParams(request.GET)

    if mparams.has_error():
        resp_info['manifest_param_error'] = mparams.get_error_message()
    else:
        # Retrieve user info
        user_info = mparams.get_user_info()
        resp_info['user_info'] = user_info

        # Retrieve dataset citation (JSON-LD)
        schema_info = mparams.get_schema_org()
        resp_info['schema_info'] = schema_info

    return render(request,
                  'dataverses/view_mock_incoming_1.html',
                  resp_info)


@login_required
def view_dataverse_incoming_2(request):
    """Test the DataverseRequestHandler"""
    resp_info = dict(title='Process Incoming Params',
                     subtitle='Example 2: Test DataverseRequestHandler',
                     incoming_params=[(k, v) for k, v in request.GET.items()])

    dv_handler = DataverseRequestHandler(request.GET, request.user)
    if dv_handler.has_error():
        resp_info['DV_HANDLER_ERROR'] = dv_handler.get_error_message()

    # Retrieve user info
    resp_info['user_info'] = dv_handler.user_info
    resp_info['schema_info'] = dv_handler.schema_info
    resp_info['schema_info_for_file'] = dv_handler.schema_info_for_file
    resp_info['dataverse_user'] = dv_handler.dataverse_user
    resp_info['dataverse_file_info'] = dv_handler.dataverse_file_info

    return render(request,
                  'dataverses/view_mock_incoming_2.html',
                  resp_info)


def view_get_info_version(request):
    """
    Mock API: Get the Dataverse version and build number.
    GET http://$SERVER/api/info/version

    reference: https://github.com/AUSSDA/pyDataverse/blob/master/src/pyDataverse/api.py#L1038
    """
    info_dict = {dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK,
                 'data': {
                     'version': '5.1.1',
                     'build': 'OpenDP App Mock API!'}
                 }
    return JsonResponse(info_dict)


def view_get_info_server(request):
    """
    Mock API: Get the Dataverse server info
    GET http://$SERVER/api/info/server

    reference: https://github.com/AUSSDA/pyDataverse/blob/master/src/pyDataverse/api.py#L90
    """
    info_dict = {dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK,
                 'data': {
                     'message': 'dataverse.MOCK-SERVER.edu'}
                 }
    return JsonResponse(info_dict)


def view_get_dataset_export(request, format='ddi'):
    """
    GET http://$SERVER/api/datasets/export?exporter=$exportformat&persistentId=$pid

    https://dataverse.harvard.edu/api/datasets/export?exporter=ddi&persistentId=doi:10.7910/DVN/PUXVDH

    https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/PUXVDH&version=1.0

    reference: https://github.com/AUSSDA/pyDataverse/blob/master/src/pyDataverse/api.py#L574
    """
    export_format = request.GET['exporter'] if 'exporter' in request.GET else None
    if export_format is not None and export_format in dv_static.EXPORTER_FORMATS:
        persistent_id = request.GET['persistentId'] if 'persistentId' in request.GET else None
        if persistent_id is None:
            return JsonResponse({dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_ERROR,
                                 dv_static.DV_KEY_MESSAGE: 'persistentId must be set'})

        mock_params = ManifestTestParams.objects.filter(datasetPid=persistent_id).first()
        if not mock_params:
            user_msg = f'ManifestTestParams object not found for persistentId {persistent_id}'
            return JsonResponse({dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_ERROR,
                                 dv_static.DV_KEY_MESSAGE: user_msg})

        # Replicate the DDI API call
        #
        """
        if export_format == dv_static.EXPORTER_FORMAT_DDI:
            if not mock_params.ddi_content:
                user_msg = f'DDI info not available for ManifestTestParams id: {mock_params.id}'
                return JsonResponse({dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_ERROR,
                                     dv_static.DV_KEY_MESSAGE: user_msg})

            ddi_download_name = f'ddi_{str(mock_params.id).zfill(5)}.xml'

            response = HttpResponse(mock_params.ddi_content, content_type='application/xml')
            response['Content-Disposition'] = f'inline;filename={ddi_download_name}'
            return response
        """

        # Replicate the schema.org API call
        #
        if export_format == dv_static.EXPORTER_FORMAT_SCHEMA_ORG:
            if not mock_params.schema_org_content:
                user_msg = f'schema.org content not available for ManifestTestParams id: {mock_params.id}'
                return JsonResponse({dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_ERROR,
                                     dv_static.DV_KEY_MESSAGE: user_msg})

            return JsonResponse(mock_params.schema_org_content)

    return JsonResponse({dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_ERROR,
                         dv_static.DV_KEY_MESSAGE: f'exporter must be one of {dv_static.EXPORTER_FORMATS}'})


def view_get_user_info(request):
    """
    Return mock user information
    """
    if not settings.DEBUG:
        return JsonResponse('TESTing only!')

    if dv_static.HEADER_KEY_DATAVERSE not in request.headers:
        user_msg = f'"{dv_static.HEADER_KEY_DATAVERSE}" key not found in the request headers'
        return JsonResponse({dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_ERROR,
                             dv_static.DV_KEY_MESSAGE: user_msg})

    user_token = request.headers[dv_static.HEADER_KEY_DATAVERSE]

    mock_params = None
    for mp in ManifestTestParams.objects.all():
        if user_token == mp.apiGeneralToken:
            mock_params = mp
            break

    if not mock_params:
        user_msg = f'ManifestTestParams not found for user_token: {user_token}'
        return JsonResponse({dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_ERROR,
                             dv_static.DV_KEY_MESSAGE: user_msg})

    if not mock_params.user_info:
        user_msg = f'User info not available for ManifestTestParams id: {mock_params.id}'
        return JsonResponse({dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_ERROR,
                             dv_static.DV_KEY_MESSAGE: user_msg})
    """
    info_dict = {
            "id": 9474,
            "identifier": "@mock_user",
            "displayName":"Mock User",
            "firstName":"Mock",
            "lastName":"User",
            "email":"mock_user@some.edu",
            "superuser":false,
            "affiliation":"Some University",
            "persistentUserId":"https://fed.some-it.some.edu/idp/shibboleth|92459eabc12ec34@some.edu",
            "createdTime":"2000-01-01T05:00:00Z",
            "lastApiUseTime":"2020-11-16T19:34:51Z",
            "authenticationProviderId":"shib"
        }
    """
    return JsonResponse({dv_static.DV_KEY_STATUS: dv_static.STATUS_VAL_OK,
                         'data': mock_params.user_info})
