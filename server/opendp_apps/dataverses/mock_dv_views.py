"""
Views meant to mimic calls by PyDataverse
"""
from django.http import JsonResponse
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

    if not mock_params.ddi_file:
        user_msg = (f'DDI file not available for ManifestTestParams id: {mock_params.id}')
        return JsonResponse({'status': 'ERROR',
                             'message': user_msg})


