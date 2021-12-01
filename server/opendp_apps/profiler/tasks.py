from django.conf import settings

from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.profiler.csv_reader import CsvReader
from opendp_apps.profiler.dataset_info_updater import DataSetInfoUpdater
from opendp_apps.profiler.profile_runner import ProfileRunner #run_profile
from opendp_apps.profiler import static_vals as pstatic
from opendp_project.celery import celery_app

from opendp_apps.dataset.models import DataSetInfo


@celery_app.task(ignore_result=True)
def run_profile_by_filepath(filepath, max_num_features=None, dataset_info_object_id=None, **kwargs):
    """Run the profiler using a valid filepath
    :filepath - filepath
    :max_column_limit - integer to limit first n columns or None for all columns
    :dataset_info_object_id - optional, id for DataSetInfo object
    """
    kwargs[pstatic.KEY_DATASET_OBJECT_ID] = dataset_info_object_id

    prunner = ProfileRunner(filepath, max_num_features, **kwargs)

    return prunner


@celery_app.task(ignore_result=True)
def run_profile_by_filefield(dataset_info_object_id, max_num_features=None, **kwargs):

    try:
        ds_info = DataSetInfo.objects.get(object_id=dataset_info_object_id)
        filefield = ds_info.source_file
    except DataSetInfo.DoesNotExist:
        filefield = None

    params = {pstatic.KEY_DATASET_IS_DJANGO_FILEFIELD: True,
              pstatic.KEY_DATASET_OBJECT_ID: dataset_info_object_id,
              pstatic.KEY_SAVE_ROW_COUNT: kwargs.get(pstatic.KEY_SAVE_ROW_COUNT, True)
              }

    prunner = ProfileRunner(filefield, max_num_features, **params)

    return prunner

