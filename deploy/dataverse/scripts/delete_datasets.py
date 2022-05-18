"""
Utility script for clearing data from a Demo Dataverse

To use this script:
(1) Set an environment variable with an API key from a Dataverse administrator
    export DV_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
(2) (Optional) Edit "datasets_to_keep.py" and add datasets to NOT delete
(3) Run "python delete_datasets.py"
    Note: this starts from the "root" dataverse and continues on down

API reference: https://dataverse.scholarsportal.info/guides/en/latest/api/native-api.html#

"""
from http import HTTPStatus
import json
import os
import requests
import sys
from typing import Union

from datasets_to_keep import DATASETS_TO_KEEP

_DV_API_KEY = os.environ.get('DV_API_KEY', 'DV_API_KEY not set.')


class DataverseDeleteUtil:
    """Convenience class for deleting Datasets"""
    _DV_LOCK_MESSAGE = 'Dataset cannot be edited due to dataset lock.'

    def __init__(self, dv_server_url, dataverse_id='root'):

        self.dv_id = dataverse_id   # example "root"
        self.server_url = self.format_url(dv_server_url)

        self.err_msg = None
        self.err_found = False

        self.num_datasets_checked = 0
        self.num_datasets_kept = 0
        self.datasets_deleted = []
        self.failed_deletes = []
        # self.dvs_deleted = []

        self.run_delete_process(self.dv_id)

    def show_stats(self):
        """Show results"""
        if self.datasets_deleted:
            print('-' * 40)
            print('Datasets deleted')
            print('-' * 40)
            for fd in self.datasets_deleted:
                print(json.dumps(fd, indent=4))
            print('-' * 40)

        if self.failed_deletes:
            print('-' * 40)
            print('Failed deletes')
            print('-' * 40)
            for fd in self.failed_deletes:
                print(json.dumps(fd, indent=4))
        print('-' * 40)

        self.msg_title(f'Datasets checked: {self.num_datasets_checked}')
        print((f'\n# kept: {self.num_datasets_kept}'
               f'\n# deleted: {len(self.datasets_deleted)}'
               f'\n# failed deletes: {len(self.failed_deletes)}'
               f'\n'
               ))

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

    @staticmethod
    def msg_title(m):
        print('-' * 40)
        print(m)
        print('-' * 40)

    def run_delete_process(self, dataverse_id):
        """List and delete the DV datasets"""
        self.msg_title('Starting Delete Process')
        print((f'server_url: {self.server_url}'
              f'\ndataverse_id: {dataverse_id}\n'))

        list_url = f'{self.server_url}/api/dataverses/{dataverse_id}/contents'

        r = requests.get(list_url, headers=self.get_dataverse_headers())

        # print(r.text)
        jresp = r.json()
        # print(json.dumps(jresp, indent=4))

        if not r.status_code == HTTPStatus.OK:
            print(json.dumps(jresp, indent=4))
            self.add_err_msg(f'Failed to list datasets. status_code: {r.status_code}')
            return

        for item in jresp['data']:
            if item['type'] == 'dataset':
                self.num_datasets_checked += 1
                if self.is_dataset_to_keep(item):
                    print((f'Keeping this dataset: {item["id"]}'
                           f'/{item["persistentUrl"]}'))
                    self.num_datasets_kept += 1
                else:
                    self.delete_dataset(item)
            elif item['type'] == 'dataverse':
                # slightly recursive...
                self.run_delete_process(item['id'])

    @staticmethod
    def is_dataset_to_keep(ds_info: dict) -> bool:
        """Given a snippet of DV Dataset information, see if it's in DATASETS_TO_KEEP"""
        if not ds_info:
            return False

        if 'persistentUrl' in ds_info:
            if ds_info['persistentUrl'] in DATASETS_TO_KEEP:
                return True

        return False

    @staticmethod
    def get_dataverse_headers():
        """Construct the header with the API key"""
        headers = {'X-Dataverse-key': _DV_API_KEY}

        return headers

    def delete_dataset_lock(self, ds_info):
        """
        Delete dataset lock and then try to re-delete the dataset
        reference: https://guides.dataverse.org/en/5.2/api/native-api.html#id69
        curl -H "X-Dataverse-key: $API_TOKEN" -X DELETE $SERVER_URL/api/datasets/$ID/locks
        """
        print('Attempt to remove lock')
        dataset_id = ds_info.get('id')
        if not dataset_id:
            self.add_err_msg(f'Dataset "id" not found in: {ds_info}')
            return

        delete_url = f'{self.server_url}/api/datasets/{dataset_id}/locks/'

        r = requests.delete(delete_url,
                            headers=self.get_dataverse_headers())

        if r.status_code == HTTPStatus.OK:
            print('Lock removed.')
            # Try to delete again!
            self.delete_dataset(ds_info, skip_lock_check=True)
        else:
            print('Failed to remove lock')
            self.failed_deletes.append(ds_info)
            print((f'\n({len(self.failed_deletes)}) Delete failure'
                   ' (couldn\'t delete lock): '))
            print('delete_url', delete_url)
            print(r.text)
            print(f'status_code: {r.status_code}')
            return

    def delete_dataset(self, ds_info, skip_lock_check=False):
        """List and delete the DV datasets"""
        if self.has_err():
            return

        # Determine whether this is a published or unpublished dataset
        #
        if 'publicationDate' in ds_info:

            # Published dataset, use the "destroy" API and persistentId
            #
            dataset_id = (f"{ds_info['protocol']}:{ds_info['authority']}"
                          f"/{ds_info['identifier']}")
            delete_url = (f'{self.server_url}/api/datasets/:persistentId/destroy/'
                          f'?persistentId={dataset_id}')
        else:
            # Unpublished dataset, use the id
            #
            dataset_id = ds_info['id']
            delete_url = f'{self.server_url}/api/datasets/{dataset_id}'

        r = requests.delete(delete_url,
                            headers=self.get_dataverse_headers())

        # print('delete result', r.text)
        print('status code', r.status_code)

        if r.status_code == HTTPStatus.OK:
            try:
                # To account for a DV error where status code was 200
                # but was returning an HTML page instead of JSON
                r.json()
                self.datasets_deleted.append(ds_info)
                print(f'dataset deleted: {dataset_id}')
            except Exception as err_obj:  # simplejson.errors.JSONDecodeError as err_obj:
                # print(type(err_obj).__name__)
                self.failed_deletes.append(ds_info)
                print(f'\n({len(self.failed_deletes)}) Delete failure w/ HTTP 200: {err_obj}')
                print('delete_url', delete_url)
                print(('Failed to convert response to JSON. Does your API'
                       ' token have administrative privileges to delete a dataset?'))
        elif r.status_code == HTTPStatus.FORBIDDEN:
            if (skip_lock_check is False) and \
              r.text.find(self._DV_LOCK_MESSAGE) > -1:
                self.delete_dataset_lock(ds_info)
            else:
                self.failed_deletes.append(ds_info)
                print(f'\n({len(self.failed_deletes)}) Delete failure: ')
                print('delete_url', delete_url)
                print(r.text)
                print(f'status_code: {r.status_code}')

        else:
            self.failed_deletes.append(ds_info)
            print(f'\n({len(self.failed_deletes)}) Delete failure: ')
            print('delete_url', delete_url)
            print(r.text)
            print(f'status_code: {r.status_code}')

    @staticmethod
    def show_instructions():
        """Print show start instructions"""
        instructions = ('Given a Dataverse id, delete its datasets as well as'
                        ' any underlying Dataverses and datasets.'
                        '\nDefault values: '
                        '\n  - server_url: https://demo-dataverse.dpcreator.org'
                        '\n  - dataverse_id: root'
                        '\n\n>>python delete_datasets.py [server_url] [dataverse_id]'
                        '\n')

        print(instructions)

    @staticmethod
    def run_delete_util(cmdline_args):
        """Run the delete process"""
        num_args = len(cmdline_args)
        # print('cmdline_args', cmdline_args)
        if num_args == 1:
            server_url = 'https://demo-dataverse.dpcreator.org'
            # server_url = 'http://dev-dataverse.dpcreator.org'
            dataverse_id = 'root'
        elif num_args == 3:
            server_url = sys.argv[1]
            dataverse_id = sys.argv[2]
        else:
            DataverseDeleteUtil.show_instructions()
            return

        delete_util = DataverseDeleteUtil(server_url, dataverse_id)

        delete_util.show_stats()
        if delete_util.has_err():
            print('Error encountered!')
            print(delete_util.err_msg)


if __name__ == '__main__':
    DataverseDeleteUtil.run_delete_util(sys.argv)
