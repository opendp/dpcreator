from django.core.exceptions import ValidationError as DjangoValidationError

from opendp_apps.dataset import static_vals as dstatic
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler.profile_runner import ProfileRunner  # run_profile
from opendp_project.celery import celery_app


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
    """
    Run the profiler using the DataSetInfo object id
    :param dataset_info_object_id DataSetInfo.object_id
    :param max_num_features int or None - number of features in the dataset to use, use None for all columns
    """
    try:
        ds_info = DataSetInfo.objects.get(object_id=dataset_info_object_id)
        filefield = ds_info.source_file
    except DataSetInfo.DoesNotExist:
        return BasicErrCheck.get_instance_with_error(dstatic.ERR_MSG_DATASET_INFO_NOT_FOUND)
    except DjangoValidationError as ex_obj:
        user_msg = f'{dstatic.ERR_MSG_INVALID_DATASET_INFO_OBJECT_ID} ({dataset_info_object_id}) ({ex_obj})'
        return BasicErrCheck.get_instance_with_error(user_msg)
    except ValueError as ex_obj:
        user_msg = f'{dstatic.ERR_MSG_INVALID_DATASET_INFO_OBJECT_ID} ({dataset_info_object_id}) ({ex_obj})'
        return BasicErrCheck.get_instance_with_error(user_msg)

    params = {pstatic.KEY_DATASET_IS_DJANGO_FILEFIELD: True,
              pstatic.KEY_DATASET_OBJECT_ID: dataset_info_object_id,
              pstatic.KEY_SAVE_ROW_COUNT: kwargs.get(pstatic.KEY_SAVE_ROW_COUNT, True)
              }

    prunner = ProfileRunner(filefield, max_num_features, **params)

    return prunner
