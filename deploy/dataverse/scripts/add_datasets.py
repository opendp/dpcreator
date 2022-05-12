"""
Utility script for clearing data from a Demo Dataverse

To use this script:
(1) Set an environment variable with an API key from a Dataverse administrator
    export DV_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
(2) Run "python add_datasets.py"
    Note: this starts from the "root" dataverse and continues on down

API reference: https://dataverse.scholarsportal.info/guides/en/latest/api/native-api.html#

"""
from http import HTTPStatus
import os
import requests
import sys
from typing import Union

_DV_API_KEY = os.environ.get('DV_API_KEY', 'DV_API_KEY not set.')


class DataverseAddDataset:
    """Convenience class for deleting Datasets"""

    def __init__(self, dv_server_url, dataverse_id, dataset_spec_fpath, file_fpath, ):

        assert os.path.isfile(dataset_spec_fpath), \
            f"dataset_spec_fpath not found/not a valid file: {dataset_spec_fpath}"
        assert os.path.isfile(file_fpath), \
            f"dataset_spec_fpath not found/not a valid file: {file_fpath}"

        self.dataset_spec_fpath = dataset_spec_fpath
        self.file_fpath = file_fpath
        self.dv_id = dataverse_id   # example "root"
        self.server_url = self.format_url(dv_server_url)

        self.new_id = None
        self.new_persistent_id = None

        self.err_msg = None
        self.err_found = False

        self.run_create_dataset_process()

    def show_result(self):
        """Show results"""
        if self.has_err():
            self.msg_title('Process failed!')
            print(self.err_msg)
        else:
            self.msg_title('Dataset published with file!')

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

    def run_create_dataset_process(self):
        """Add a dataset, add a file to it, and publish the dataset"""
        if self.has_err():
            return

        if not self.add_dataset():
            return

        if not self.add_file_and_publish():
            return

    def add_dataset(self):
        """Add the dataset via its JSOn spec"""
        if self.has_err():
            return False

        self.msg_title('Add Dataset')
        add_dataset_url = f'{self.server_url}/api/dataverses/{self.dv_id}/datasets'

        print('add_dataset_url', add_dataset_url)
        ds_content = open(self.dataset_spec_fpath, 'r').read()

        r = requests.post(add_dataset_url,
                          headers=self.get_dataverse_headers(),
                          data=ds_content)

        if r.status_code != HTTPStatus.CREATED:
            self.add_err_msg(f'Failed to create dataset. {r.text}\n{r.status_code}')
            return False

        jresp = r.json()
        print('jresp', jresp)
        self.new_id = jresp['data']['id']
        self.new_persistent_id = jresp['data']['persistentId']

        return True

    def add_file_and_publish(self):
        """Add a file to the dataset"""
        if self.has_err():
            return False

        self.msg_title('Add File')

        file_content = open(self.file_fpath, 'r').read()
        files = {'file': (os.path.basename(self.file_fpath), file_content)}

        add_file_url = (f'{self.server_url}/api/datasets/:persistentId/add?'
                        f'persistentId={self.new_persistent_id}')

        r = requests.post(add_file_url,
                          headers=self.get_dataverse_headers(),
                          files=files)

        if r.status_code != HTTPStatus.OK:
            self.add_err_msg(f'Failed to add file to dataset. {r.text}\n{r.status_code}')
            return False

        print('File added!')

        self.msg_title('Publish Dataset')

        publish_url = (f'{self.server_url}/api/datasets/:persistentId/actions/:publish?'
                       f'persistentId={self.new_persistent_id}&type=major')

        print('publish_url', publish_url)

        r = requests.post(publish_url,
                          headers=self.get_dataverse_headers())
        # print(r.text)
        # print(r.status_code)

        if r.status_code != HTTPStatus.OK:
            self.add_err_msg(f'Failed to publish dataset. {r.text}\n{r.status_code}')
            return False

        print('Dataset published!')

    @staticmethod
    def get_dataverse_headers():
        """Construct the header with the API key"""
        headers = {'X-Dataverse-key': _DV_API_KEY}

        return headers

    @staticmethod
    def show_instructions():
        """Print show start instructions"""
        instructions = ('\nCreate a dataset with a file, and publish it'
                        '\nDefault values: '
                        '\n  - server_url: https://demo-dataverse.dpcreator.org'
                        '\n  - dataverse_id: root'
                        '\n  - dataset_spec_file_path: dataset_specs/pums_fulton.json'
                        '\n  - dataset_file_path: dataset_specs/pums_1000.csv'
                        '\n\n(1) >> python delete_datasets.py'
                        '\n\n(2) >> python delete_datasets.py [dataset_spec_file_path] [dataset_file_path]'
                        '\n\n(3) >> python delete_datasets.py [server_url] [dataverse_id]'
                        ' [dataset_spec_file_path] [dataset_file_path]'
                        '\n')

        print(instructions)

    @staticmethod
    def run_add_util(cmdline_args):
        """Run the delete process"""
        num_args = len(cmdline_args)
        if num_args == 1:
            server_url = 'https://demo-dataverse.dpcreator.org'
            dataverse_id = 'root'
            dataset_spec_fpath = 'dataset_specs/pums_fulton.json'
            dataset_file_fpath = 'dataset_specs/pums_1000.csv'
        elif num_args == 3:
            server_url = 'https://demo-dataverse.dpcreator.org'
            dataverse_id = 'root'
            dataset_spec_fpath = sys.argv[1]
            dataset_file_fpath = sys.argv[2]
        elif num_args == 5:
            server_url = sys.argv[1]
            dataverse_id = sys.argv[2]
            dataset_spec_fpath = sys.argv[3]
            dataset_file_fpath = sys.argv[4]
        else:
            DataverseAddDataset.show_instructions()
            return

        print(server_url, dataverse_id, dataset_spec_fpath, dataset_file_fpath)

        add_util = DataverseAddDataset(server_url,
                                       dataverse_id,
                                       dataset_spec_fpath,
                                       dataset_file_fpath)

        add_util.show_result()

if __name__ == '__main__':
   DataverseAddDataset.run_add_util(sys.argv)

"""
python add_datasets.py dataset_specs/pums_fulton.json dataset_specs/pums_1000.csv
"""
