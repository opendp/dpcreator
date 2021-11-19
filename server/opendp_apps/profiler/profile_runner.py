from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.profiler.dataset_info_updater import DataSetInfoUpdater
from opendp_apps.profiler.variable_info import VariableInfoHandler


def run_profile(df, dataset_info_object_id):
    """
    Process dataframe for variable profiling, while updating the DatasetInfo object at each step
    :param df:
    :param dataset_info_object_id:
    :return: VariableInfoHandler
    """
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
