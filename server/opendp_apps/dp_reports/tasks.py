"""
Run the PDF report maker async
"""
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.dataset import static_vals as dstatic

from opendp_apps.profiler.profile_runner import ProfileRunner #run_profile
from opendp_apps.profiler import static_vals as pstatic
from opendp_project.celery import celery_app

from opendp_apps.analysis.models import ReleaseInfo
from opendp_apps.dp_reports.pdf_report_maker import PDFReportMaker

@celery_app.task(ignore_result=True)
def run_pdf_report_maker(release_info_object_id, websocket_id=None, **kwargs):
    """
    Create a PDF file and save it to the ReleaseInfo object
    """
    print('run_pdf_report_maker 1')
    try:
        release_info = ReleaseInfo.objects.get(object_id=release_info_object_id)
        print('run_pdf_report_maker 2')
    except ReleaseInfo.DoesNotExist:
        print('run_pdf_report_maker 3')
        return {'success': False,
                'message': f'ReleaseInfo object not found. {release_info_object_id}'}

    # -------------------------------
    # Create the release PDF
    # -------------------------------
    print('run_pdf_report_maker 4')
    report_maker = PDFReportMaker(release_info.dp_release)
    print('run_pdf_report_maker 5')
    if report_maker.has_error():
        print('run_pdf_report_maker 6')

        return {'success': False,
                'message': report_maker.get_err_msg()}

    print('run_pdf_report_maker 7')

    report_maker.save_pdf_to_release_obj(release_info)
    print('run_pdf_report_maker 8')
    return {'success': True,
            'message': f'PDF created and saved to the ReleaseInfo object'}


