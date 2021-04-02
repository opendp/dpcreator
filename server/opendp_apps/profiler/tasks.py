from opendp_project.celery import celery_app

from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.profiler.profile_handler import ProfileHandler
from opendp_apps.profiler import static_vals as pstatic


@celery_app.task(ignore_result=True)
def run_profile_by_filepath(filepath, dataset_object_id=None):
    """Run the profiler using a valid filepath"""
    params = {pstatic.KEY_DATASET_IS_FILEPATH: True}

    params[pstatic.KEY_DATASET_OBJECT_ID] = dataset_object_id

    ph = ProfileHandler(dataset_pointer=filepath, **params)

    return ph


@celery_app.task(ignore_result=True)
def run_profile_by_filefield(dataset_info_object_id, **kwargs):
    """Run the profiler using a valid filepath"""
    params = {pstatic.KEY_DATASET_IS_DJANGO_FILEFIELD: True,
              pstatic.KEY_DATASET_OBJECT_ID: dataset_info_object_id,
              'websocket_id': kwargs.get('websocket_id', None)}

    try:
        ds_info = DataSetInfo.objects.get(object_id=dataset_info_object_id)
        filefield = ds_info.source_file
    except DataSetInfo.DoesNotExist:
        filefield = None

    ph = ProfileHandler(dataset_pointer=filefield, **params)

    return ph
