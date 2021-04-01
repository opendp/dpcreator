import requests_mock

from opendp_apps.dataverses.dataverse_client import DataverseClient
from opendp_apps.dataverses.models import DataverseHandoff
from opendp_apps.dataverses.testing.test_endpoints import BaseEndpointTest
from opendp_apps.model_helpers.msg_util import msgt


@requests_mock.Mocker()
class FileViewGetTest(BaseEndpointTest):

    def test_get_schema_org(self, req_mocker):
        msgt(self.test_get_schema_org.__doc__)
        self.set_mock_requests(req_mocker)

        handoff = DataverseHandoff.objects.first()
        # print(handoff.siteUrl, handoff.apiGeneralToken)
        client = DataverseClient(handoff.siteUrl, handoff.apiGeneralToken)
        schema_org_content = client.get_schema_org(handoff.datasetPid)
        # print(f"response: {schema_org_content.__dict__}")
        self.assertIsNotNone(schema_org_content.json())
        self.assertEquals(schema_org_content.status_code, 200)