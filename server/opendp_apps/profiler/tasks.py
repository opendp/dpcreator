from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.profiler.csv_reader import CsvReader
from opendp_apps.profiler.dataset_info_updater import DataSetInfoUpdater
from opendp_apps.profiler.variable_info import VariableInfoHandler
from opendp_project.celery import celery_app

from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.profiler.profile_handler import ProfileHandler
from opendp_apps.profiler import static_vals as pstatic


@celery_app.task(ignore_result=True)
def run_profile_by_filepath(filepath, dataset_object_id=None, **kwargs):
    """Run the profiler using a valid filepath"""
    params = {pstatic.KEY_DATASET_IS_FILEPATH: True}

    params[pstatic.KEY_DATASET_OBJECT_ID] = dataset_object_id
    params[pstatic.KEY_SAVE_ROW_COUNT] = kwargs.get(pstatic.KEY_SAVE_ROW_COUNT, True)
    df = CsvReader(filepath).read()
    dataset_info = None
    dataset_info_updater = None

    if dataset_object_id:
        dataset_info = DataSetInfo.objects.get(object_id=dataset_object_id)
        dataset_info_updater = DataSetInfoUpdater(dataset_info)

    try:
        ph = VariableInfoHandler(df)
        if dataset_info:
            dataset_info_updater.update_step(DepositorSetupInfo.DepositorSteps.STEP_0300_PROFILING_PROCESSING)
        ph.run_profile_process()
    except Exception as ex:
        if dataset_info:
            dataset_info_updater.update_step(DepositorSetupInfo.DepositorSteps.STEP_9300_PROFILING_FAILED)
        raise ex
    if dataset_info:
        dataset_info_updater.save_data_profile(ph.data_profile)
        dataset_info_updater.update_step(DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE)

    return ph


@celery_app.task(ignore_result=True)
def run_profile_by_filefield(dataset_info_object_id, **kwargs):
    """Run the profiler using a valid filepath"""
    params = {pstatic.KEY_DATASET_IS_DJANGO_FILEFIELD: True,
              pstatic.KEY_DATASET_OBJECT_ID: dataset_info_object_id,
              pstatic.KEY_SAVE_ROW_COUNT: kwargs.get(pstatic.KEY_SAVE_ROW_COUNT, True)
              }

    try:
        ds_info = DataSetInfo.objects.get(object_id=dataset_info_object_id)
        filefield = ds_info.source_file
    except DataSetInfo.DoesNotExist:
        filefield = None

    ph = ProfileHandler(dataset_pointer=filefield, **params)

    return ph

