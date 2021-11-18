from opendp_apps.dataset.models import DataSetInfo


class DataSetInfoUpdater:

    def __init__(self, dataset_info: DataSetInfo):
        self.dataset_info = dataset_info

    def update_step(self, step):
        self.dataset_info.depositor_setup_info.set_user_step(step)
        self.dataset_info.depositor_setup_info.save()

    def save_data_profile(self, data_profile):
        self.dataset_info.data_profile = data_profile
        self.dataset_info.profile_variables = data_profile
        self.dataset_info.save()