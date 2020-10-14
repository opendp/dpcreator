import lxml.etree as etree

from pyDataverse.api import Api


class DataverseClient(object):

    def __init__(self, host):
        self._host = host
        self.api = Api(host)

    def get_ddi(self, doi):
        """
        Get DDI metadata file
        """
        response = self.api.get_dataset_export(doi, 'ddi')
        return response.content


class DDI(object):

    def __init__(self, ddi_string):
        """
        ddi_string: result from get_ddi in DataverseClient
        """
        self.xml_tree = etree.fromstring(ddi_string)


if __name__ == '__main__':

    host = 'https://dataverse.harvard.edu'
    client = DataverseClient(host)
    doi = 'doi:10.7910/DVN/GEWLZD'
    ddi_string = client.get_ddi('doi:10.7910/DVN/GEWLZD')

    ddi_obj = DDI(ddi_string)

    print(etree.tostring(ddi_obj.xml_tree, pretty_print=True, encoding="unicode"))
