from load_django_settings import CURRENT_DIR, TEST_DATA_DIR, load_local_settings
load_local_settings()

import requests

def get_test_params():
    """Sample params"""
    params = dict(apiGeneralToken='4484985a-32c9-4366-81d2-79662f9ae37e',
                  site_url='http://host.docker.internal:8089',
                  datasetPid='doi:10.5072/FK2/9WIC1Y',
                  fileId=10,
                  )
    return params

def post_test_data():
    """Test post"""
    dpcreator_host = 'http://localhost:8000'

    # dpcreator_url = f'{dpcreator_host}/dv-mock-api/test-dv-post'  # reflect back (UI)
    dpcreator_url = f'{dpcreator_host}/api/dv-handoff/dv_orig_create/'  # actual url

    headers = {'signedUrl': ('http://host.docker.internal:8089'
                             '?until=2022-04-25T14:57:01.889'
                             '&user=dataverseAdmin'
                             '&method=POST'
                             '&token=9bbab6a12cc926ee94ac023f743c528b51d4387c36'
                             'ca9b6ffc6bc3444e74e1a976b0495d842bf1a23e2d7'
                             'c22c761eb20f230fdd11ace3ef0a40bd8e73b0b9150')}

    r = requests.post(dpcreator_url,
                      headers=headers,
                      data=get_test_params())

    print('status_code', r.status_code)
    print(r.text)


if __name__ == '__main__':
    post_test_data()
