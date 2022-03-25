from load_django_settings import CURRENT_DIR, TEST_DATA_DIR, load_local_settings
load_local_settings()

import uuid
from opendp_apps.dp_reports.pdf_report_maker import PDFReportMaker


def make_test_report():
    rm = PDFReportMaker(None, uuid.uuid4())
    rm.save_pdf_to_file()


if __name__ == '__main__':
    make_test_report()
