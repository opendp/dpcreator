from opendp_apps.dataset.models import DataSetInfo


class DataSetInfoUpdater:

    def __init__(self, dataset_info: DataSetInfo):
        """
        Wrapper for common DataSetInfo operations
        :param dataset_info:
        """
        self.dataset_info = dataset_info

    def update_step(self, step):
        """
        Set the step to a new value
        :param step:
        :return:
        """
        self.dataset_info.depositor_setup_info.set_user_step(step)
        self.dataset_info.depositor_setup_info.save()

    def save_data_profile(self, data_profile):
        """
        Add a new associated data profile
        :param data_profile:
        :return:
        """
        self.dataset_info.data_profile = data_profile
        self.dataset_info.profile_variables = data_profile
        self.dataset_info.save()
