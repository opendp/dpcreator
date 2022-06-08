"""
Format a DataSetInfo for use in a JSON Release
"""
import json

from django.core.serializers.json import DjangoJSONEncoder

from opendp_apps.analysis.misc_formatters import get_readable_datetime
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp, BasicResponse


class DataSetFormatter(BasicErrCheck):

    def __init__(self, dataset_info: DataSetInfo):
        """Init with a DataSetInfo object"""
        assert isinstance(dataset_info, DataSetInfo), '"dataset_info" must be a DataSetInfo instance.'

        self.dataset = dataset_info
        self.formatted_info = {}

        self.run_formatter()

    def run_formatter(self):
        """
        Format the dataset info
        """
        if self.dataset.source == DataSetInfo.SourceChoices.UserUpload:
            self.dataset = self.dataset.uploadfileinfo  # Get the UploadFileInfo object
            self.format_user_upload()
        elif self.dataset.source == DataSetInfo.SourceChoices.Dataverse:
            self.dataset = self.dataset.dataversefileinfo  # Get the DataverseFileInfo object
            self.format_dataverse_dataset()
        else:
            self.add_err_msg('Unknown dataset type: {self.dataset.source}')
            return

    def get_formatted_info(self, as_json=False):
        """
        Return the formatted data
        """
        assert self.has_error() is False, \
            "Do not call this method before checking if \".has_error()\" is False"

        if as_json:
            return json.dumps(self.formatted_info, cls=DjangoJSONEncoder, indent=4)

        return self.formatted_info

    def format_user_upload(self):
        """Format UserUpload dataset"""
        if self.has_error():
            return

        ds_dict = {
            'type': self.dataset.source,
            'name': self.dataset.name,
            'fileFormat': self.dataset.get_file_type(),
            'creator': self.dataset.creator.as_json(),  # OpenDP User object
            "upload_date": {
                "iso": self.dataset.created.isoformat(),
                "human_readable": get_readable_datetime(self.dataset.created),
                "human_readable_date_only": self.dataset.created.strftime('%-d %B, %Y'),
            },
        }

        self.formatted_info = ds_dict

    def format_dataverse_dataset(self):
        """Format UserUpload dataset"""
        if self.has_error():
            return

        # Pull citation from self.dataset.dataset_schema_info
        #
        citation_info = self.get_citation_from_dataset_schema_or_none()
        if citation_info.success:
            citation = citation_info.data
        else:
            self.add_err_msg(citation_info.message)
            return

        # Pull name from self.dataset.dataset_schema_info
        #
        name_info = self.get_name_from_dataset_schema()
        if name_info.success:
            ds_name = name_info.data
        else:
            self.add_err_msg(name_info.message)
            return

        # Format info in self.dataset.file_schema_info
        #
        file_info = self.get_file_info()
        if file_info.success:
            file_dict = file_info.data
        else:
            self.add_err_msg(file_info.message)
            return

        ds_dict = {
            'type': self.dataset.source,
            'name': self.dataset.name,
            "citation": citation,
            "doi": self.dataset.dataset_doi,
            "identifier": self.get_dataset_identifier_or_none(),
            'installation': {
                "name": self.dataset.dv_installation.name,
                "url": self.dataset.dv_installation.dataverse_url
            },
            "file_information": file_dict
        }

        self.formatted_info = ds_dict

    def get_name_from_dataset_schema(self) -> BasicResponse:
        """
        Return the "name" text from self.dataset_schema_info (a bit ugly...)
        Trying to return string from: self.dataset.dataset_schema_info['name']
        """
        if self.has_error():
            # Shouldn't happen...
            return err_resp(self.get_err_msg())

        if not self.dataset.dataset_schema_info:
            return err_resp('".dataset_schema_info" is empty')

        if 'name' not in self.dataset.dataset_schema_info:
            return err_resp('"name" not found in ".dataset_schema_info" not found')

        ds_name = self.dataset.dataset_schema_info['name']
        if not ds_name:
            return err_resp('"name" within ".dataset_schema_info" is empty')

        return ok_resp(ds_name)

    def get_dataset_identifier_or_none(self):
        """Return the identifer within dataset_schema_info['identifer']"""
        if '@id' in self.dataset.dataset_schema_info['@id']:
            return self.dataset.dataset_schema_info['@id']

        return None

    def get_citation_from_dataset_schema_or_none(self):
        """
        Return the citation text from self.dataset_schema_info (a bit ugly...)
        Trying to return string from: self.dataset.dataset_schema_info['citation'][0]
        """
        if self.has_error():
            # Shouldn't happen...
            return err_resp(self.get_err_msg())

        if not self.dataset.dataset_schema_info:
            return err_resp('".dataset_schema_info" is empty')

        if 'citation' not in self.dataset.dataset_schema_info:
            return ok_resp(None)

        # If the citation key is found, then do error checking....
        if (not self.dataset.dataset_schema_info['citation']) or \
                (not isinstance(self.dataset.dataset_schema_info['citation'], list)):
            return err_resp('"citation" within ".dataset_schema_info" is empty or not a list')

        if 'text' not in self.dataset.dataset_schema_info['citation'][0]:
            return err_resp('"[\'citation\'][0][\'text\']" not found in ".dataset_schema_info"')

        return ok_resp(self.dataset.dataset_schema_info['citation'][0]['text'])

    def get_file_info(self):
        """
        Return information from the "DataverseFileInfo.file_schema_info" field
        Ideal:
        {
            "name": "crisis.tab"
            "identifier": "https://doi.org/10.7910/DVN/OLD7MB/ZI4N3J",
            "fileFormat": "text/tab-separated-values",
        }
        """
        if self.has_error():
            # Shouldn't happen!
            return err_resp(self.get_err_msg())

        if not self.dataset.file_schema_info:
            return err_resp('".file_schema_info" is empty')

        file_dict = {}

        if 'name' in self.dataset.file_schema_info:
            file_dict['name'] = self.dataset.file_schema_info['name']
        else:
            return err_resp('"name" not found in ".file_schema_info" not found')

        if 'identifier' in self.dataset.file_schema_info:
            file_dict['identifier'] = self.dataset.file_schema_info['identifier']
        else:
            file_dict['identifier'] = None

        if 'fileFormat' in self.dataset.file_schema_info:
            file_dict['fileFormat'] = self.dataset.file_schema_info['fileFormat']
        else:
            file_dict['fileFormat'] = None

        return ok_resp(file_dict)
