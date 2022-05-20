"""
Run the PDF report maker async
"""
import logging

from django.conf import settings

from opendp_project.celery import celery_app

from opendp_apps.analysis.models import ReleaseInfo
from opendp_apps.dp_reports.pdf_report_maker import PDFReportMaker


logger = logging.getLogger(settings.DEFAULT_LOGGER)


@celery_app.task(ignore_result=True)
def run_pdf_report_maker(release_info_object_id, websocket_id=None, **kwargs):
    """
    Create a PDF file and save it to the ReleaseInfo object
    """
    try:
        release_info = ReleaseInfo.objects.get(object_id=release_info_object_id)
    except ReleaseInfo.DoesNotExist:
        logger.error(f'ReleaseInfo object not found. {release_info_object_id}')
        return {'success': False,
                'message': f'ReleaseInfo object not found. {release_info_object_id}'}

    # -------------------------------
    # Create the release PDF
    # -------------------------------
    report_maker = PDFReportMaker(release_info.dp_release)
    if report_maker.has_error():
        logger.error(report_maker.get_err_msg())
        return {'success': False,
                'message': report_maker.get_err_msg()}

    report_maker.save_pdf_to_release_obj(release_info)
    logger.info('PDF created and saved to the ReleaseInfo object')
    return {'success': True,
            'message': f'PDF created and saved to the ReleaseInfo object'}


