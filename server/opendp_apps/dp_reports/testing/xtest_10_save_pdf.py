import json

from os.path import abspath, dirname, isfile, join

CURRENT_DIR = dirname(abspath(__file__))
TEST_DATA_DIR = join(dirname(dirname(dirname(CURRENT_DIR))), 'test_data')

from django.contrib.auth import get_user_model
from django.core.files import File
from django.test.testcases import TestCase

from rest_framework.test import APIClient
from rest_framework.reverse import reverse as drf_reverse

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan, AuxiliaryFileDepositRecord
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.validate_release_util import ValidateReleaseUtil
from opendp_apps.analysis.release_info_formatter import ReleaseInfoFormatter
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.dataset.dataset_formatter import DataSetFormatter
from opendp_apps.model_helpers.msg_util import msgt
from opendp_apps.profiler import tasks as profiler_tasks
from opendp_apps.profiler import  static_vals as pstatic
from opendp_apps.utils.extra_validators import VALIDATE_MSG_EPSILON

from borb.pdf.document import Document
from borb.pdf.page.page import Page
from borb.pdf.canvas.layout.page_layout.multi_column_layout import SingleColumnLayout
from borb.pdf.canvas.layout.page_layout.page_layout import PageLayout
from borb.pdf.canvas.layout.text.paragraph import Paragraph
from borb.pdf.pdf import PDF
from borb.pdf.canvas.color.color import HexColor

class TestRunRelease(TestCase):
    fixtures = ['test_dataset_data_001.json']

    def setUp(self):
        # test client
        self.client = APIClient()

        self.user_obj, _created = get_user_model().objects.get_or_create(username='dev_admin')

        self.client.force_login(self.user_obj)

        dataset_info = DataSetInfo.objects.get(id=4)
        # self.add_source_file(dataset_info, 'Fatigue_data.tab', True)

    def test_10_compute_stats(self):
        """(10) Run compute stats"""
        msgt(self.test_10_compute_stats.__doc__)

        doc: Document = Document()
        page: Page = Page()
        doc.append_page(page)
        layout: PageLayout = SingleColumnLayout(page)

        # construct the Font object
        # font_path: Path = Path(__file__).parent / "Jsfont-Regular.ttf"
        # font: Font = TrueTypeFont.true_type_font_from_file(font_path)

        layout.add(Paragraph("Hello World!"))
        layout.add(Paragraph("Hello World!",
                             font="Times-roman",
                             font_color=HexColor("#86CD82")))

        # ----------------------------------
        dataset_info = DataSetInfo.objects.get(id=4)

        import io
        from django.core.files.base import ContentFile

        # example:
        pdf_bytes = io.BytesIO()
        PDF.dumps(pdf_bytes, doc)
        pdf_bytes.seek(0)

        dataset_info.source_file.save('ye_release.pdf',
                                      ContentFile(pdf_bytes.read()))
        dataset_info.save()

        print('dataset_info.source_file', dataset_info.source_file)

