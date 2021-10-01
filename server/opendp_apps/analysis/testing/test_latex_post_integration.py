import requests

from django.test import TestCase

from opendp_apps.analysis.latex_request_formatter import LatexRequestFormatter
from opendp_apps.analysis.models import ReleaseInfo


class TestLatexRequestFormatter(TestCase):

    fixtures = ['test_release_001.json',]

    def test_post(self):
        release = ReleaseInfo.objects.first()
        latex_request_formatter = LatexRequestFormatter(release)
        data = latex_request_formatter.format()
        response = requests.post('http://latex:1234/', json=data)
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(list(json_response.keys()), ['key', 'object_id'])
