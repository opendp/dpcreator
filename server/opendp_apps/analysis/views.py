from rest_framework import viewsets


class BaseStepUpdaterView(viewsets.ViewSet):
    """
    Idea: keep next_step as view property to tell each endpoint how
    to update the status
    """

    @property
    def next_step(self):
        """
        This should be an enum from DepositorSteps
        """
        return NotImplementedError

