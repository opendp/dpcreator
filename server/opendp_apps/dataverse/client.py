from pprint import pprint

import lxml.etree as etree

from pyDataverse.api import Api


class DataverseClient(object):

    def __init__(self, host, api_token=None):
        self._host = host
        self.api = Api(host, api_token=api_token)

    def get_ddi(self, doi, format='ddi'):
        """
        Get DDI metadata file
        """
        response = self.api.get_dataset_export(doi, format)
        return DDI(response.content)


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

    client = DataverseClient(host)
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