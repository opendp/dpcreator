from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.profiler.csv_reader import CsvReader
from opendp_apps.profiler.dataset_info_updater import DataSetInfoUpdater
from opendp_apps.profiler.variable_info import VariableInfoHandler
from opendp_project.celery import celery_app

from opendp_apps.dataset.models import DataSetInfo


def run_profile(df, dataset_info_object_id):
    dataset_info = None
    dataset_info_updater = None

    if dataset_info_object_id:
        dataset_info = DataSetInfo.objects.get(object_id=dataset_info_object_id)
        dataset_info_updater = DataSetInfoUpdater(dataset_info)

    try:
        ph = VariableInfoHandler(df)
        if dataset_info:
            if dataset_info.depositor_setup_info.user_step < DepositorSetupInfo.DepositorSteps.STEP_0300_PROFILING_PROCESSING:
                dataset_info_updater.update_step(DepositorSetupInfo.DepositorSteps.STEP_0300_PROFILING_PROCESSING)
        ph.run_profile_process()

    except Exception as ex:
        if dataset_info:
            dataset_info_updater.update_step(DepositorSetupInfo.DepositorSteps.STEP_9300_PROFILING_FAILED)
        raise ex
    if dataset_info:
        dataset_info_updater.save_data_profile(ph.data_profile)
        if dataset_info.depositor_setup_info.user_step < DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE:
            dataset_info_updater.update_step(DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE)

    return ph


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
