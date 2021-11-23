from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.profiler.csv_reader import CsvReader
from opendp_apps.profiler.dataset_info_updater import DataSetInfoUpdater
from opendp_apps.profiler.profile_runner import run_profile
from opendp_project.celery import celery_app

from opendp_apps.dataset.models import DataSetInfo


@celery_app.task(ignore_result=True)
def run_profile_by_filepath(filepath, dataset_info_object_id=None, **kwargs):
    """Run the profiler using a valid filepath"""
    df = CsvReader(filepath).read()
    return run_profile(df, dataset_info_object_id)


@celery_app.task(ignore_result=True)
def run_profile_by_filefield(dataset_info_object_id):
    try:
        ds_info = DataSetInfo.objects.get(object_id=dataset_info_object_id)
        filefield = ds_info.source_file
    except DataSetInfo.DoesNotExist:
        filefield = None
    try:
        df = CsvReader(filefield.path).read()
    except Exception as ex:
        if dataset_info_object_id:
            dataset_info = DataSetInfo.objects.get(object_id=dataset_info_object_id)
            dataset_info_updater = DataSetInfoUpdater(dataset_info)
            dataset_info_updater.update_step(DepositorSetupInfo.DepositorSteps.STEP_9300_PROFILING_FAILED)
        raise ex
    return run_profile(df, dataset_info_object_id)
