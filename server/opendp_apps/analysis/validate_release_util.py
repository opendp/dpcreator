"""
- Build computation chain from user-created statistic specifications
    - Validate computation
    - Run computation
- Flow:
    - Given an AnalysisPlan object_id an opendp_user
    - Retrieve the AnalysisPlan and make sure the opendp_user created it
        - Retrieve the max epsilon from analysis_plan.dataset.depositor_setup_info.epsilon
        - Retrieve the max delta from analysis_plan.dataset.depositor_setup_info.delta
    - Iterate through the specs in the AnalysisPlan.dp_statistics
        - Retrieve the variable type/min/max/categories from AnalysisPlan.variable_info
        - Retrieve
"""
import pkg_resources

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from opendp.mod import OpenDPException
from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.stat_valid_info import StatValidInfo
#from opendp_apps.analysis.tools.dp_mean import dp_mean
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis.tools.dp_mean_spec import DPMeanSpec
from opendp_apps.analysis.tools.dp_spec_error import DPSpecError
from opendp_apps.utils.extra_validators import \
    (validate_epsilon_not_null,
     validate_not_negative)
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck

# Temp workaround!!! See Issue #300
# https://github.com/opendp/dpcreator/issues/300
from opendp_apps.utils.camel_to_snake import camel_to_snake



class ValidateReleaseUtil(BasicErrCheck):

    def __init__(self, opendp_user: get_user_model(), analysis_plan_id: int, dp_statistics: list, release_run=False, **kwargs):
        """Passing IDs instead of objects here makes it easier to run async via celery, etc."""
        self.opendp_user = opendp_user     # to be retrieved

        self.analysis_plan_id = analysis_plan_id
        self.analysis_plan = None       # to be retrieved

        self.max_epsilon = None         # from analysis_plan.dataset.get_depositor_setup_info()
        self.max_delta = None           # from analysis_plan.dataset.get_depositor_setup_info()
        self.dataset_size = None        # from analysis_plan.dataset

        self.dp_statistics = dp_statistics  # User defined

        self.stat_spec_list = []      # list of StatSpec objects
        self.validation_info = []     # list of StatValidInfo objects to send to UI
        self.release_stats = []

        self.opendp_version = pkg_resources.get_distribution('opendp').version

        self.run_validation_process()

        if release_run:
            pass
            # do some more stuff
            # self.run_release()



    def add_stat_spec(self, stat_spec: StatSpec):
        """Add a StatSpec subclass to a list"""
        self.stat_spec_list.append(stat_spec)


    def run_release_process(self):
        """Run the release process"""
        if self.has_error():
            return

        # Run it again!!!
        self.run_validation_process()
        if self.has_error():
            return

        self.release_stats = []
        col_indexes = self.get_variable_indices()
        if col_indexes is None: # error already set
            return

        # Call run_chain
        #
        for stat_spec in self.stat_spec_list:
            file_info = self.analysis_plan.dataset.source_file
            file_obj = open(file_info, 'r')
            stat_spec.run_chain(col_indexes, file_obj, sep_char="\t")
            if stat_spec.has_error():
                print('error! stop process!')
                print(stat_spec.get_error_messages())
                del(self.release_stats)
                return

            self.release_stats.append(stat_spec.get_release_dict())

        print('self.release_stats', self.release_stats)

    def run_validation_process(self):
        """Run the validation"""
        if not self.run_preliminary_steps():
            return

        # Make sure the variable indices are available!
        # Not needed in this step but required for computation
        #
        if self.get_variable_indices() is None:
            # error already set
            return

        self.build_stat_specs()
        if not self.stat_spec_list:
            self.add_err_msg('No statistics were built!')
            return

        # Iterate through the stat specs and validate them!
        #
        running_epsilon = 0.0
        for stat_spec in self.stat_spec_list:
            # Check each stat_spec
            if not stat_spec.is_chain_valid():
                # Nope: invalid!
                self.validation_info.append(stat_spec.get_error_msg_dict())
            else:
                # Looks good but check single stat epsilon and cumulative epsilon
                #
                running_epsilon += stat_spec.epsilon
                if stat_spec.epsilon > self.max_epsilon:
                    # Error one stat uses more than all the epsilon!
                    #
                    user_msg = (f'The epsilon ({stat_spec.epsilon}) exceeds'
                                f' max epsilon ({self.max_epsilon})')
                    stat_spec.add_err_msg(user_msg)
                    self.validation_info.append(stat_spec.get_error_msg_dict())

                elif  running_epsilon > self.max_epsilon:
                    # Error: Too much epsilon used!
                    #
                    user_msg = (f'The running epsilon ({running_epsilon}) exceeds'
                                f' the max epsilon ({self.max_epsilon})')
                    stat_spec.add_err_msg(user_msg)
                    self.validation_info.append(stat_spec.get_error_msg_dict())
                else:
                    # Looks good!
                    self.validation_info.append(stat_spec.get_success_msg_dict())


    def get_variable_indices(self):
        """
        Retrieve variable indices from the dataset profile
        Needed for actual data calculation!

        Returns variable_indices or None!
        """
        variable_indices_info = self.analysis_plan.dataset.get_variable_order(as_indices=True)
        if variable_indices_info.success:
            return variable_indices_info.data

        self.add_err_msg(variable_indices_info.message)
        return None


    def build_stat_specs(self):
        """
        Build a list of StatSpec subclasses that can be used for
        chain validation or running computations
        """
        # Iterate through the stats!
        #
        self.stat_spec_list = []
        stat_num = 0

        # track total epsilon
        #
        running_epsilon = 0

        for dp_stat in self.dp_statistics:
            stat_num += 1       # not used yet...
            """
            We're putting together lots of properties to pass to 
            statistic specific classes such as DPMeanSpec.
            
            These classes take care of most error checking and validation.
            
            - Some sample input from the UI--e.g. contents of "dp_stat:
                {
                    "statistic": astatic.DP_MEAN,
                    "variable": "EyeHeight",
                    "epsilon": 1,
                    "delta": 0,
                    "error": "",
                    "missing_values_handling": astatic.MISSING_VAL_INSERT_FIXED,
                    "handle_as_fixed": False,
                    "fixed_value": "5.0",
                    "locked": False,
                    "label": "EyeHeight"},
            """
            # -------------------------------------
            # (1) Begin building the property dict
            # -------------------------------------
            props = dp_stat         # start with what is in dp_stat--the UI input
            props['dataset_size'] = self.dataset_size   # add dataset size
            props['impute_constant'] = dp_stat.get('fixed_value') # one bit of renaming!

            #  Some high-level error checks, before making the StatSpec
            #
            variable = props.get('variable')
            statistic = props.get('statistic', 'shrug?')
            epsilon = props.get('epsilon')

            # (1) Is variable defined?
            #
            if not props.get('variable'):
                props['error_message'] = (f'"variable" is missing from this'
                                          f'DP Stat specification.')
                self.add_stat_spec(DPSpecError(props))
                continue  # to the next dp_stat specification

            # (2) Is this a known statistic? If not stop here.
            #
            if not statistic in astatic.DP_STATS_CHOICES:
                # also checked in the DPStatisticSerializer
                props['error_message'] = f'Statistic "{statistic}" is not supported'
                self.add_stat_spec(DPSpecError(props))
                continue  # to the next dp_stat specification


            # (3) Add variable_info which has min/max/categories, variable type, etc.
            #
            variable_info = self.analysis_plan.variable_info.get(variable)
            if not variable_info:
                # Temp workaround!!! See Issue #300
                # https://github.com/opendp/dpcreator/issues/300
                variable_info = self.analysis_plan.variable_info.get(camel_to_snake(variable))

            if variable_info:
                props['variable_info'] = variable_info
            else:
                props['error_message'] = 'Variable info not found.'
                self.add_stat_spec(DPSpecError(props))
                continue  # to the next dp_stat specification

            # (4) Retrieve the column index
            #
            col_idx_info = self.analysis_plan.dataset.get_variable_index(variable)
            if col_idx_info.success:
                props['col_index'] = col_idx_info.data
            else:
                props['error_message'] = col_idx_info.message
                self.add_stat_spec(DPSpecError(props))
                continue  # to the next dp_stat specification

            # Okay, "props" are built! Let's see if they work!
            #
            if statistic == astatic.DP_MEAN:
                self.add_stat_spec(DPMeanSpec(props))
                continue
            elif statistic == astatic.DP_COUNT:
                props['error_message'] = (f'Statistic "{statistic}" will be'
                                          f' supported soon!')
                self.add_stat_spec(DPSpecError(props))
                continue
            elif statistic in astatic.DP_STATS_CHOICES:
                props['error_message'] = (f'Statistic "{statistic}" will be supported'
                                          f' soon!')
                self.add_stat_spec(DPSpecError(props))
                continue
            else:
                # Shouldn't reach here, unknown stats are captured up above
                pass


    def run_preliminary_steps(self):
        """Run preliminary steps before validation"""

        # Retrieve the Analysis Plan
        #
        ap_info = AnalysisPlanUtil.retrieve_analysis(self.analysis_plan_id, self.opendp_user)
        if not ap_info.success:
            self.add_err_msg(ap_info.message)
            return False

        self.analysis_plan = ap_info.data

        # Check the dp_statistics spec
        #
        if not self.dp_statistics:
            user_msg = 'There are no statistics to validate'
            self.add_err_msg(ap_info.message)
            return False

        dataset_size_info = self.analysis_plan.dataset.get_dataset_size()
        if dataset_size_info.success:
            self.dataset_size = dataset_size_info.data
        else:
            self.add_err_msg('Dataset size is not available')
            return False

        # Make sure the total epsilon is valid
        #
        self.max_epsilon = self.analysis_plan.dataset.get_depositor_setup_info().epsilon
        self.max_delta = self.analysis_plan.dataset.get_depositor_setup_info().delta

        epsilon_ok, _err_msg_or_None = self.is_epsilon_valid(self.max_epsilon)
        if not epsilon_ok:
            user_msg = f'{astatic.ERR_MSG_BAD_TOTAL_EPSILON}: {self.max_epsilon}'
            self.add_err_msg(user_msg)
            return False

        try:
            validate_not_negative(self.max_delta)
        except ValidationError as err_obj:
            user_msg = f'{astatic.ERR_MSG_BAD_TOTAL_DELTA}: {self.max_delta}'
            self.add_err_msg(user_msg)
            return False


        return True

    def is_epsilon_valid(self, val):
        """Validate a val as epsilon"""
        try:
            validate_epsilon_not_null(val)
        except ValidationError as err_obj:
            return False, str(err_obj)

        return True, None