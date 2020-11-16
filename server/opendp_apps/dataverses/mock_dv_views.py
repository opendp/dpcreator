"""
Views meant to mimic calls by PyDataverse
"""
import json
from django.http import HttpResponse, JsonResponse
from opendp_apps.dataverses.models import ManifestTestParams
from opendp_apps.dataverses.dataverse_manifest_params import DataverseManifestParams
from opendp_apps.dataverses import static_vals as dv_static

def view_dataverse_incoming(request):
    """Do something with incoming DV info ..."""

    # user id
    # call dV api

    outlines = []
    if request.GET:
        for k, v in request.GET.items():
            if v:
                outlines.append(f'<br /><br /><b>{k}</b>: {v}')
            else:
                outlines.append(f'<br /><br /><b>{k}</b>: (not set)')

    if not outlines:
        return HttpResponse('No GET params found')

    mparams = DataverseManifestParams(request.GET)
    if mparams.has_error():
        return HttpResponse(mparams.get_error_message())
        #print(mparams.get_error_message())

    schema_info = mparams.get_schema_org()
    return HttpResponse(schema_info)
    return HttpResponse('\n'.join(outlines))



def view_get_info_version(request):
    """
    Mock API: Get the Dataverse version and build number.
    GET http://$SERVER/api/info/version

    reference: https://github.com/AUSSDA/pyDataverse/blob/master/src/pyDataverse/api.py#L1038
    """
    info_dict = {'status': 'OK',
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
    info_dict = {'status': 'OK',
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
    exportFormat = request.GET['exporter'] if 'exporter' in request.GET else None
    if exportFormat is None or not exportFormat in dv_static.EXPORTER_FORMATS:
        return JsonResponse({'status': 'ERROR',
                             'message': f'exporter must be one of {dv_static.EXPORTER_FORMATS}'})

    persistentId = request.GET['persistentId'] if 'persistentId' in request.GET else None
    if persistentId is None:
        return JsonResponse({'status': 'ERROR',
                             'message': 'persistentId must be set'})


    mock_params = ManifestTestParams.objects.filter(datasetPid=persistentId).first()
    if not mock_params:
        user_msg = (f'ManifestTestParams not found for persistentId {persistentId}')
        return JsonResponse({'status': 'ERROR',
                             'message': user_msg})

    # Replicate the DDI API call
    #
    if exportFormat == dv_static.EXPORTER_FORMAT_DDI:
        if not mock_params.ddi_content:
            user_msg = (f'DDI info not available for ManifestTestParams id: {mock_params.id}')
            return JsonResponse({'status': 'ERROR',
                                 'message': user_msg})

        ddi_download_name = f'ddi_{str(mock_params.id).zfill(5)}.xml'

        response = HttpResponse(mock_params.ddi_content, content_type='application/xml')
        response['Content-Disposition'] = f'inline;filename={ddi_download_name}'

    # Replicate the schema.org API call
    #
    elif exportFormat == dv_static.EXPORTER_FORMAT_SCHEMA_ORG:
        if not mock_params.schema_org_content:
            user_msg = (f'schema.org content not available for ManifestTestParams id: {mock_params.id}')
            return JsonResponse({'status': 'ERROR',
                                 'message': user_msg})

        return JsonResponse({'status': 'OK',
                             'message': json.dumps(mock_params.schema_org_content)})

    return response


def view_get_user_info(request):
    """
    Return mock user information
    """
    if dv_static.HEADER_KEY_DATAVERSE not in request.headers:
        user_msg = (f'"{dv_static.HEADER_KEY_DATAVERSE}" key not found in the request headers')
        return JsonResponse({'status': 'ERROR',
                             'message': user_msg})

    user_token = request.headers[dv_static.HEADER_KEY_DATAVERSE]

    mock_params = ManifestTestParams.objects.filter(apiGeneralToken=user_token).first()
    if not mock_params:
        user_msg = (f'ManifestTestParams not found for user_token: {user_token}')
        return JsonResponse({'status': 'ERROR',
                             'message': user_msg})

    if not mock_params.user_info:
        user_msg = (f'User info not available for ManifestTestParams id: {mock_params.id}')
        return JsonResponse({'status': 'ERROR',
                             'message': user_msg})
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
    return JsonResponse({'status': 'OK',
                         'data': mock_params.user_info})
