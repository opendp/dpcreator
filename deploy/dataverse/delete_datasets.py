"""
Utility script for clearing data from a Demo Dataverse

To use this script:
(1) Set an environment variable with an API key from a Dataverse administrator
    export API_TOKEN=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
(2) to do: add list of datset exceptions
(3) Run "python delete_datasets.py"
    Note: this starts from the "root" dataverse and continues on down

API reference: https://dataverse.scholarsportal.info/guides/en/latest/api/native-api.html#

"""
import json
import os
import requests
from typing import Union

_DV_API_KEY = os.environ.get('DV_API_KEY', 'DV_API_KEY not set.')

class DataverseDeleteUtil:

    def __init__(self, server_url, dv_id='root'):

        self.dv_id = dv_id  # example "root"
        self.server_url = self.format_url(server_url)

        self.err_msg = None
        self.err_found = False

        self.run_delete_process(self.dv_id)

    @staticmethod
    def format_url(url_str: str) -> Union[str, None]:
        """Lowercase and trim trailing slash"""
        if not url_str:
            return None

        while url_str.endswith('/'):
            if url_str:
                url_str = url_str[:-1]

        return url_str.lower()

    def has_err(self) -> bool:
        """Return state of err_found"""
        return self.err_found

    def add_err_msg(self, m):
        self.err_found = True
        self.err_msg = m

    def run_delete_process(self, dataverse_id):
        """List and delete the DV datasets"""
        list_url = f'{self.server_url}/api/dataverses/{dataverse_id}/contents'

        r = requests.get(list_url, headers=self.get_dataverse_headers())

        # print(r.text)
        jresp = r.json()
        print(json.dumps(jresp, indent=4))

        print('r.status_code', r.status_code)

        for item in jresp['data']:
            if item['type'] == 'dataset':
                self.delete_dataset(item)
            elif item['type'] == 'dataverse':
                # slightly recursive...
                self.run_delete_process(item['id'])

    def get_dataverse_headers(self):
        """Construct the header with the API key"""
        headers = {'X-Dataverse-key': _DV_API_KEY}

        return headers

    def delete_dataset(self, ds_info):
        """List and delete the DV datasets"""
        print('delete_dataset; ds_info', ds_info)
        # Determine whether this is a published or unbpublished dataset
        #
        if 'publicationDate' in ds_info:

            # Published dataset, use the "destroy" API and persistentId
            #
            persistent_id = (f"{ds_info['protocol']}:{ds_info['authority']}"
                             f"/{ds_info['identifier']}")
            delete_url = (f'{self.server_url}/api/datasets/:persistentId/destroy/'
                          f'?persistentId={persistent_id}')
        else:
            # Unpublished dataset, use the id
            #
            dataset_id = ds_info['id']
            delete_url = f'{self.server_url}/api/datasets/{dataset_id}'

        print('delete_url', delete_url)
        r = requests.delete(delete_url,
                            headers=self.get_dataverse_headers())

        print(r.text)
        print(r.status_code)


if __name__=='__main__':

    server_url = 'https://demo-dataverse.dpcreator.org'
    dv_id = 'root'

    delete_util = DataverseDeleteUtil(server_url, dv_id)

