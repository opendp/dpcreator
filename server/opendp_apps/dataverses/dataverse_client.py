import json
from pprint import pprint

import requests
from requests.exceptions import ConnectionError
import lxml.etree as etree

from pyDataverse.api import Api, DataAccessApi, NativeApi

from opendp_apps.dataverses import static_vals as dv_static
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp


class DataverseClient(object):

    def __init__(self, host, api_token=None):
        self._host = host
        self.api_token = api_token
        self.api = Api(host, api_token=api_token)
        self.native_api = NativeApi(host, api_token=api_token)
        self.data_access_api = DataAccessApi(host, api_token=api_token)

    def get_ddi(self, doi, format=dv_static.EXPORTER_FORMAT_DDI):
        """
        Get DDI metadata file
        """
        response = self.native_api.get_dataset_export(doi, format)
        return DDI(response.content)

    def get_user_info(self, user_api_token=None):
        """
        Placeholder until pyDataverse API is updated
        """
        api_token = user_api_token if user_api_token else self.api_token
        # remove any trailing "/"
        ye_host = self._host
        while ye_host.endswith('/'):
            ye_host = ye_host[:-1]

        # format url
        dv_url = f'{ye_host}/api/v1/users/:me'

        # make the request
        headers = {'X-Dataverse-key': api_token}
        try:
            response = requests.get(dv_url, headers=headers)
        except ConnectionError as err_obj:
            return err_resp(f'Failed to connect. {err_obj}')

        if response.status_code == 200:
            resp_json = response.json()
            dv_status = resp_json.get(dv_static.DV_KEY_STATUS)
            if not dv_status:
                return err_resp(f"Dataverse response failed to return a 'status'.")

            if dv_status == dv_static.STATUS_VAL_ERROR:
                user_msg = resp_json.get(dv_static.DV_KEY_MESSAGE,
                                         '(No message from Dataverse)')
                return err_resp(f"Dataverse error: {user_msg}")

            return ok_resp(response.json())

        try:
            json_resp = response.json()
            if 'message' in json_resp:
                return err_resp(json_resp['message'])
        except ValueError:
            pass
        return err_resp(f'Status code: {response.status_code} {response.text}')

    def get_schema_org(self, doi):
        """
        Get schema.org data
        """
        return self.get_dataset_export_json(doi, dv_static.EXPORTER_FORMAT_SCHEMA_ORG)

    def get_dataset_export_json(self, doi, format_type):
        """
        Get dataset export
        """
        try:
            response = self.native_api.get_dataset_export(doi, format_type)
        except ConnectionError as err_obj:
            return err_resp(f'Failed to connect. {err_obj}')


        if response.status_code == 200:
            try:
                json_resp = response.json()

                # Is there an error message in the response?
                if dv_static.DV_KEY_STATUS in json_resp:
                    if json_resp[dv_static.DV_KEY_STATUS] == dv_static.STATUS_VAL_ERROR:
                        # why, yes there is
                        return err_resp(json_resp[dv_static.DV_KEY_MESSAGE])
                else:
                    return ok_resp(json_resp)
            except ValueError:
                pass

        #print('response.status_code', response.status_code)
        return err_resp(f'Dataset export failed for format {format_type}',
                        response.content)
'''
    def get_data_file_by_id(self, file_id):
        """Return the Dataverse using the file id"""
        return self.get_data_file(file_id, is_pid=False)

    def get_data_file_by_doi(self, file_doi):
        """Return the Dataverse using the file DOI"""
        return self.get_data_file(file_doi)


    def get_data_file(self, identifier, is_pid=True):
        """Return the Dataverse using the file id or file DOI
        ref: https://github.com/gdcc/pyDataverse/blob/master/src/pyDataverse/api.py#L298
        """
        try:
            response = self.native_api.get_datafile(identifier, is_pid=is_pid)
        except ConnectionError as err_obj:
            return err_resp(f'Failed to connect. {err_obj}')

        if response.status_code == 200:
            return
        self.data_access_api.get_datafile(identifier)
'''

class DDI(object):

    def __init__(self, ddi_string):
        """
        ddi_string: result from get_ddi in DataverseClient
        """
        self.xml_tree = etree.XML(ddi_string)

    def __call__(self, *args, **kwargs):
        return self.xml_tree

    def __str__(self):
        return etree.tostring(self.xml_tree, pretty_print=True, encoding="unicode")

    def get_title(self):
        return self.xml_tree.find('.//{ddi:codebook:2_5}titl').text

    def get_data_descriptions(self):
        """
        Construct a dictionary of summary statistics for
        each variable in the dataset
        """
        data_description_nodes = self.xml_tree.find('{ddi:codebook:2_5}dataDscr').getchildren()
        descs = {}
        for description in data_description_nodes:
            id, name, interval = description.attrib['ID'], description.attrib['name'], description.attrib['intrvl']
            descs[id] = {'name': name, 'interval': interval}
            sum_stats = description.findall('{ddi:codebook:2_5}sumStat')
            for stat in sum_stats:
                stat_type = stat.attrib['type']
                # TODO: Better way to convert to None?
                descs[id][stat_type] = stat.text if stat.text != 'NaN' else None
        # TODO: Option to return this as dataframe?
        return descs


if __name__ == '__main__':

    host = 'https://dataverse.harvard.edu'
    doi = 'doi:10.7910/DVN/GEWLZD'

    # This file must be completed with a valid Dataverse API token
    with open('dataverse_token.json', 'r') as infile:
        api_token = json.load(infile).get('token')

    client = DataverseClient(host, api_token=api_token)
    ddi_obj = client.get_ddi(doi)

    with open('example.ddi', 'w') as outfile:
        outfile.write(ddi_obj.__str__())

    heading = "Title: " + ddi_obj.get_title()
    print()
    print(''.join(["-" for _ in range(0, len(heading))]))
    print(heading)
    print(''.join(["-" for _ in range(0, len(heading))]))

    print()
    print("Data Description Example: ")
    descriptions = ddi_obj.get_data_descriptions()
    key = list(descriptions.keys())[0]
    print('ID: ', key)
    pprint(descriptions[key])

    # print(ddi_obj.get_title())
    print()
    resp = client.get_user_info(api_token)
    #print(resp.__dict__)

"""
from pyDataverse.api import Api
host = 'https://dataverse.harvard.edu'
api = Api(host)
#self.api = Api(host, api_token=api_token)

api.get_info_version()

"""
