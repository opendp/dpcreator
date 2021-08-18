from django.contrib.auth import get_user_model
from rest_framework import status

from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.analysis.models import AnalysisPlan

from opendp_apps.model_helpers.basic_response import BasicResponse, ok_resp, err_resp


class AnalysisPlanUtil:
    """Functions used by API endpoints"""

    @staticmethod
    def create_plan(dataset_object_id: str, opendp_user: get_user_model()) -> BasicResponse:
        """
        Create an AnalysisPlan object
        Input: DatasetInfo.object_id
        Initial settings:
            analyst - logged in user
            user_step - (initial step, check branch)
            variable_info - default to DepositorSetup values
        """
        if not dataset_object_id:
            return err_resp('dataset_object_id not set', data=status.HTTP_400_BAD_REQUEST)
        if not isinstance(opendp_user, get_user_model()):
            return err_resp('opendp_user not set', data=status.HTTP_400_BAD_REQUEST)


        # -------------------------------
        # Retrieve DataSetInfo object
        # -------------------------------
        try:
            ds_info = DataSetInfo.objects.get(object_id=dataset_object_id,
                                              creator=opendp_user)
        except DataSetInfo.DoesNotExist:
            user_msg = 'DataSetInfo object not found for this object_id and creator'
            return err_resp(user_msg, data=status.HTTP_400_BAD_REQUEST)


        # ------------------------------------
        # Is the DepositorSetupInfo complete?
        # ------------------------------------
        depositor_info = DataSetInfo.depositor_setup_info
        if not depositor_info.is_complete:
            user_msg = 'Depositor setup is not complete'
            return err_resp(user_msg, data=status.HTTP_422_UNPROCESSABLE_ENTITY)


        # ------------------------------------
        # Create the plan!
        # ------------------------------------
        plan = AnalysisPlan(analyst=opendp_user,
                            name='plan 1',  # need a better name here!
                            dataset=ds_info,
                            is_complete=False,
                            user_set=AnalysisPlan.AnalystSteps.STEP_0500_VARIABLES_CONFIRMED)

        plan.save()

        return ok_resp('Plan created!', data=plan)