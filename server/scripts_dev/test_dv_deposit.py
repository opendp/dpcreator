from load_django_settings import CURRENT_DIR, TEST_DATA_DIR, load_local_settings
load_local_settings()

import json, time
from os.path import isfile, join

from opendp_project.celery import hello_task
from django.core.serializers.json import DjangoJSONEncoder
from opendp_apps.dataverses.dataverse_deposit_util import DataverseDepositUtil
from opendp_apps.analysis.models import ReleaseInfo
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.dataset.models import DataverseFileInfo
from opendp_apps.dataverses.dataverse_download_handler import DataverseDownloadHandler


def build_test_data():
    """
    Semi-manual run here to create a ReleaseInfo object and
    DataverseUser based on an existing dummy DataverseFileInfo object
    """
    df = DataverseFileInfo.objects(pk=some_pk)


def test_dv_depositor(release_id):
    """Test profiler with file"""

    try:
        release_info = ReleaseInfo.objects.get(id=release_id)
    except ReleaseInfo.DoesNotExist:
        print(f'Failed to find ReleaseInfo using id: {release_id}')
        return

    print('get object')
    deposit_util = DataverseDepositUtil(release_info=release_info)
    if deposit_util.has_error():
        print('Deposit Error! ', deposit_util.get_err_msg())
        return
    else:
        print('looks good!')

def run_deposit_api():
    """
    Run direct API
    """
    # https://guides.dataverse.org/en/latest/developers/aux-file-support.html
    #
    import dv_test_creds as dv_cred
    import requests
    """
    export API_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    export FILENAME='auxfile.txt'
    export FILE_ID='12345'
    export FORMAT_TAG='dpJson'
    export FORMAT_VERSION='v1'
    export TYPE='DP'
    export SERVER_URL=https://demo.dataverse.org
    """

    #curl -H X-Dataverse-key:$API_TOKEN -X POST -F "file=@$FILENAME" -F 'origin=myApp' -F 'isPublic=true' -F "type=$TYPE" "$SERVER_URL/api/access/datafile/$FILE_ID/auxiliary/$FORMAT_TAG/$FORMAT_VERSION"
    """
    """
    #curl

    headers = {'X-Dataverse-key': dv_cred.API_TOKEN}

    FORMAT_TAG = 'dpJSON' #dpPDF'  # 'dp-c-JSON', 'dpJSON
    FORMAT_VERSION = 'v11'  # '.json'

    dv_url = dv_cred.SERVER_URL
    if not dv_url.endswith('/'):
        dv_url += '/'
    dv_url = (f'{dv_url}api/access/datafile/{dv_cred.FILE_ID}'
              f'/auxiliary/{FORMAT_TAG}/{FORMAT_VERSION}')

    #    FORMAT_TAG = 'dp-c-JSON'
    #   FORMAT_VERSION = '.json'

    #fname = 'report_mean_income.pdf'    \
    fname = 'deposit_01.json'
    full_fname = join(TEST_DATA_DIR, 'deposit', fname)

    payload = dict(origin='DP Creator',
                   isPublic=True,
                   type=dv_cred.TYPE)

    if not isfile(full_fname):
        print(f'file not found: {full_fname}')
        return

    files = {'file': open(full_fname, 'rb')}

    print('dv_url', dv_url)
    response = requests.post(dv_url,
                             headers=headers,
                             data=payload,
                             files=files)

    print('status_code: ', response.status_code)
    print('response.text', response.text)
    print('-' * 40)
    try:
        print('response json', response.json())
    except Exception as ex_obj:
        print('ex_obj', ex_obj)
        print('could not convert to JSON')




if __name__=='__main__':
    # test_dv_depositor(release_id=5)
    run_deposit_api()
