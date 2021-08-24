from django.contrib.auth import get_user_model
from rest_framework import status

from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis import static_vals as astatic

from opendp_apps.utils.randname import get_rand_alphanumeric
from opendp_apps.model_helpers.basic_response import BasicResponse, ok_resp, err_resp


class AnalysisPlanUtil:
    """Functions used by API endpoints"""

    @staticmethod
    def retrieve_analysis(analysis_object_id: str,  opendp_user: get_user_model()) -> BasicResponse:
        """
        Retrieve an existing AnalysisPlan object by it's object_id and analyst
        """
        if not analysis_object_id:
            return err_resp(astatic.ERR_MSG_ANALYSIS_ID_REQUIRED,
                            data=status.HTTP_400_BAD_REQUEST)
        if not isinstance(opendp_user, get_user_model()):
            return err_resp(astatic.ERR_MSG_USER_REQUIRED,
                            data=status.HTTP_400_BAD_REQUEST)

        # -------------------------------
        # Retrieve AnalysisPlan object
        # -------------------------------
        try:
            plan = AnalysisPlan.objects.get(object_id=analysis_object_id,
                                              analyst=opendp_user)
        except AnalysisPlan.DoesNotExist:
            return err_resp(astatic.ERR_MSG_NO_ANALYSIS_PLAN,
                            data=status.HTTP_400_BAD_REQUEST)

        return ok_resp(plan, message='Plan created!')


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
            return err_resp(astatic.ERR_MSG_DATASET_ID_REQUIRED,
                            data=status.HTTP_400_BAD_REQUEST)
        if not isinstance(opendp_user, get_user_model()):
            return err_resp(astatic.ERR_MSG_USER_REQUIRED,
                            data=status.HTTP_400_BAD_REQUEST)

        # -------------------------------
        # Retrieve DataSetInfo object
        # -------------------------------
        try:
            ds_info = DataSetInfo.objects.get(object_id=dataset_object_id,
                                              creator=opendp_user)
        except DataSetInfo.DoesNotExist:
            return err_resp(astatic.ERR_MSG_NO_DATASET,
                            data=status.HTTP_400_BAD_REQUEST)


        # ------------------------------------
        # Is the DepositorSetupInfo complete?
        # ------------------------------------
        depositor_info = ds_info.depositor_setup_info
        if not depositor_info.is_complete:
            return err_resp(astatic.ERR_MSG_SETUP_INCOMPLETE,
                            data=status.HTTP_422_UNPROCESSABLE_ENTITY)


        # ------------------------------------
        # Create the plan!
        # ------------------------------------
        plan = AnalysisPlan(\
                analyst=opendp_user,
                name=f'Plan {get_rand_alphanumeric(7)}',  # need a better name here!
                dataset=ds_info,
                is_complete=False,
                variable_info=ds_info.depositor_setup_info.variable_info,
                user_step=AnalysisPlan.AnalystSteps.STEP_0700_VARIABLES_CONFIRMED)

        plan.save()

        return ok_resp(plan, message='Plan created!')