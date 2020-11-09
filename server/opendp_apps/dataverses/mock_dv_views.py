"""
Views meant to mimic calls by PyDataverse
"""
from django.http import HttpResponse, JsonResponse
from opendp_apps.dataverses.models import ManifestTestParams

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
    if exportFormat is None or not exportFormat == 'ddi':
        return JsonResponse({'status': 'ERROR',
                             'message': 'exporter must be "ddi"'})

    persistentId = request.GET['persistentId'] if 'persistentId' in request.GET else None
    if persistentId is None:
        return JsonResponse({'status': 'ERROR',
                             'message': 'persistentId must be set'})


    mock_params = ManifestTestParams.objects.filter(datasetPid=persistentId).first()
    if not mock_params:
        user_msg = (f'ManifestTestParams not found for persistentId {persistentId}')
        return JsonResponse({'status': 'ERROR',
                             'message': user_msg})

    if not mock_params.ddi_content:
        user_msg = (f'DDI info not available for ManifestTestParams id: {mock_params.id}')
        return JsonResponse({'status': 'ERROR',
                             'message': user_msg})

    ddi_download_name = f'ddi_{str(mock_params.id).zfill(5)}.xml'

    response = HttpResponse(mock_params.ddi_content, content_type='application/xml')
    response['Content-Disposition'] = f'inline;filename={ddi_download_name}'

    return response


def view_get_user_info(request, user_token):
    """
    Return mock user information
    """
    mock_params = ManifestTestParams.objects.filter(apiGeneralToken=user_token).first()
    if not mock_params:
        user_msg = (f'ManifestTestParams not found for user_token: {user_token}')
        return JsonResponse({'status': 'ERROR',
                             'message': user_msg})

    info_dict = {
            "authenticationProviderId": "builtin",
            "persistentUserId": "mockUser",
            "position": "Depositor",
            "id": 114,
            "identifier": "@mockUser",
            "displayName": "Mock User",
            "firstName": "Mock",
            "lastName": "User",
            "email": "mockUser@some.edu",
            "superuser": False,
            "affiliation": "Dataverse.org"
        }

    return JsonResponse({'status': 'OK',
                         'data': info_dict})
