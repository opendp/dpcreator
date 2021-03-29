from opendp_project.celery import celery_app

from opendp_apps.profiler.profile_handler import ProfileHandler
from opendp_apps.profiler import static_vals as pstatic


@celery_app.task(ignore_result=True)
def run_profile_by_filepath(filepath, dataset_object_id=None):
    """Run the profiler using a valid filepath"""
    params = {pstatic.KEY_DATASET_IS_FILEPATH: True}

    params[pstatic.KEY_DATASET_OBJECT_ID] = dataset_object_id

    ph = ProfileHandler(dataset_pointer=filepath, **params)

    return ph

    # if ph.has_error():
    #    print(f'error: {ph.get_err_msg()}')
    # else:
    #   print('profiled!')
