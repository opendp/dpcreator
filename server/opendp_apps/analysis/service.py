from opendp_apps.dataset.models import DepositorSetupInfo


class StepUpdater(object):

    def __init__(self, depositor_setup_info: DepositorSetupInfo, ):
        """
        Update the user_step on a given DepositorSetupInfo
        """
        self._depositor_setup_info = depositor_setup_info

    def update_step(self, step_size=1):
        """
        Increment step by step_size (default 1)
        """
        if step_size == 0:
            raise ValueError("step_size must be greater or less than 0")
        step_list = list(DepositorSetupInfo.DepositorSteps)
        current_step = self._depositor_setup_info.user_step
        new_index = step_list.index(current_step) + step_size
        new_step = step_list[new_index]
        # In case we've entered the part of the enum where errors are,
        # just ignore and don't update
        if 'error' not in new_step.value:
            self._depositor_setup_info.user_step = new_step
            self._depositor_setup_info.save()
