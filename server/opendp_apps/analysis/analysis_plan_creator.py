from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.exceptions import EpsilonNotSetException, AllottedEpsilonExceedsLimit
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.dataset.depositor_setup_helpers import get_selected_variable_info
from opendp_apps.dataset.models import DatasetInfo
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck


class AnalysisPlanCreator(BasicErrCheck):
    """Create an AnalysisPlan object"""

    def __init__(self, opendp_user: get_user_model(), plan_info: dict):
        """Create an AnalysisPlan object"""

        # DatasetInfo.object_id (not AnalysisPlan.object_id)
        #
        self.dataset_object_id = plan_info.get('object_id')
        self.opendp_user = opendp_user

        # dict w/ analyst_id, name, epsilon, expiration_date, description for new AnalysisPlan
        #
        self.plan_info = plan_info

        # Variables to format/create
        self.new_analyst_id = None  # object_id of the OpenDPUser who will be the analyst
        self.new_name = None
        self.new_epsilon = None
        self.new_expiration_date = None
        self.new_description = None

        self.analyst_user_obj = None
        self.dataset_info = None
        self.available_epsilon = None
        self.analysis_plan = None

        self.run_create_plan_process()

    def run_create_plan_process(self):
        """Create an AnalysisPlan object after running through a series of checks"""

        self.run_initial_checks()
        if self.has_error():
            return

        self.create_plan()

    def run_initial_checks(self):
        """Run initial checks and gather preliminary data to create the AnalysisPlan object"""
        if not self.dataset_object_id:
            self.add_err_msg(astatic.ERR_MSG_DATASET_ID_REQUIRED)
            return

        if not isinstance(self.opendp_user, get_user_model()):
            self.add_err_msg(astatic.ERR_MSG_USER_REQUIRED)
            return

        # -------------------------------
        # Retrieve the DatasetInfo object and make sure setup is complete
        # -------------------------------
        try:
            self.dataset_info = DatasetInfo.objects.get(object_id=self.dataset_object_id,
                                                        creator=self.opendp_user)
        except DatasetInfo.DoesNotExist:
            self.add_err_msg(astatic.ERR_MSG_NO_DATASET)
            return

        # Is set up complete?
        if not self.dataset_info.depositor_setup_info.is_complete:
            self.add_err_msg(astatic.ERR_MSG_SETUP_INCOMPLETE)
            return

        if not isinstance(self.plan_info, dict):
            self.add_err_msg(astatic.ERR_MSG_PLAN_INFO_REQUIRED)
            return

        # ---------------------------------
        # check analyst_id
        # ---------------------------------

        # Is the analyst_id set?
        #
        self.new_analyst_id = self.plan_info.get('analyst_id')
        if self.new_analyst_id is None:
            # No analyst_id specified, default to the current user
            #
            self.new_analyst_id = self.opendp_user.object_id
            self.analyst_user_obj = self.opendp_user

        elif self.new_analyst_id == self.opendp_user.object_id:
            # The analyst_id is the same as the current user
            self.analyst_user_obj = self.opendp_user

        else:
            # There's an analyst_id, make sure it's a valid user
            try:
                self.analyst_user_obj = get_user_model().objects.get(object_id=self.new_analyst_id)
            except get_user_model().DoesNotExist:
                self.add_err_msg(astatic.ERR_MSG_PLAN_INFO_ANALYST_ID_INVALID)
                return

        # check that epsilon is an int or a float and > 0
        self.new_epsilon = self.plan_info.get('epsilon')
        if not (type(self.new_epsilon) == int or type(self.new_epsilon) == float):
            self.add_err_msg(astatic.ERR_MSG_PLAN_INFO_EPSILON_MISSING)
            return

        if self.new_epsilon <= 0:
            self.add_err_msg(astatic.ERR_MSG_PLAN_INFO_EPSILON_MISSING)
            return

        # check name
        self.new_name = self.plan_info.get('name')
        if not isinstance(self.new_name, str) or len(self.new_name) == 0:
            self.add_err_msg(astatic.ERR_MSG_PLAN_INFO_NAME_MISSING)
            return

        # check description (optional, default to empty string)
        self.new_description = self.plan_info.get('description')
        if not isinstance(self.new_name, str) or len(self.new_name) == 0:
            self.new_description = ''

        # check expiration date
        new_expiration_date_str = str(self.plan_info.get('expiration_date'))
        # TODO: Is this date > current date?
        try:
            self.new_expiration_date = datetime.strptime(new_expiration_date_str, '%Y-%m-%d')
            self.new_expiration_date = make_aware(self.new_expiration_date)
        except ValueError:
            self.add_err_msg(
                astatic.ERR_MSG_PLAN_INFO_EXPIRATION_DATE_INVALID.format(expiration_date=new_expiration_date_str))
            return

        # Is there remaining epsilon for this dataset?
        available_epsilon = self.get_available_epsilon(self.dataset_info)
        if available_epsilon == 0:
            self.add_err_msg(astatic.ERR_MSG_NO_EPSILON_AVAILABLE)
            return

        # Is there enough epsilon for this new AnalysisPlan?
        if available_epsilon - self.new_epsilon < 0:
            user_msg = astatic.ERR_MSG_NOT_ENOUGH_EPSILON_AVAILABLE.format(available_epsilon=available_epsilon,
                                                                           requested_epsilon=self.new_epsilon)
            self.add_err_msg(user_msg)
            return

    def create_plan(self):
        """Create the AnalysisPlan object!"""
        if self.has_error():
            return

        var_info_resp = get_selected_variable_info(self.dataset_info.depositor_setup_info.variable_info)
        if not var_info_resp.success:
            self.add_err_msg(var_info_resp.message)
            return

        params = dict(analyst=self.analyst_user_obj,
                      dataset=self.dataset_info,
                      variable_info=var_info_resp.data,
                      confidence_level=self.dataset_info.depositor_setup_info.confidence_level,
                      name=self.new_name,
                      description=self.new_description,
                      epsilon=self.new_epsilon,
                      expiration_date=self.new_expiration_date,
                      user_step=AnalysisPlan.AnalystSteps.STEP_0000_INITIALIZED)

        self.analysis_plan = AnalysisPlan(**params)

        self.analysis_plan.save()

    @staticmethod
    def get_available_epsilon(dataset: DatasetInfo) -> float:
        """
        Get the available epsilon for a dataset by totaling epsilon allotted to AnalysisPlans
        """
        allotted_epsilon = 0
        for plan in AnalysisPlan.objects.filter(dataset=dataset):
            if not plan.epsilon:
                raise EpsilonNotSetException((f'AnalysisPlan object has no epsilon value. (analysis plan:'
                                              f' {plan.object_id})'))
            allotted_epsilon += plan.epsilon

        available_epsilon = dataset.depositor_setup_info.epsilon - allotted_epsilon
        if available_epsilon < 0:
            raise AllottedEpsilonExceedsLimit((f'Available epsilon is less than zero.'
                                               f' (dataset: {dataset.object_id})'))

        return available_epsilon
