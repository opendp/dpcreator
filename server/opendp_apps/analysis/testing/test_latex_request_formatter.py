from django.test import TestCase

from opendp_apps.analysis.latex_request_formatter import LatexRequestFormatter
from opendp_apps.analysis.models import ReleaseInfo


class TestLatexRequestFormatter(TestCase):

    fixtures = ['test_release_001.json', ]

    def test_format(self):
        release = ReleaseInfo.objects.first()
        latex_request_formatter = LatexRequestFormatter(release)
        request = latex_request_formatter.format()
        self.assertEqual(list(request.keys()), ['statistics', 'histograms', 'object_id', 'base_filename'])
