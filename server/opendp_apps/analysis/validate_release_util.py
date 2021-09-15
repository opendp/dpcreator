"""Utility class utilized by DRF API endpoints"""

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from opendp.mod import OpenDPException
from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.stat_valid_info import StatValidInfo
from opendp_apps.analysis.tools.dp_mean import dp_mean
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis.tools.dp_mean_spec import DPMeanSpec
from opendp_apps.utils.extra_validators import \
    (validate_epsilon_not_null,)
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

        self.max_epsilon = None         # from DepositorSetupInfo

        self.dp_statistics = dp_statistics

        self.validation_info = []      # list of StatValidInfo objects as dicts to return to UI

        self.run_validation_process()

        if release_run:
            pass
            # do some more stuff
            # self.run_release()


    def run_release(self):
        """Run the release process"""
        if self.has_error():
            return

        self.run_validation_process()


    def run_validation_process(self):
        """Run the validation"""
        if not self.run_preliminary_steps():
            return

        # Iterate through the stats!
        #
        self.validation_info = []
        stat_num = 0


        running_epsilon = 0
        # max_epsilon - set in run_preliminary_steps

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
            variable = dp_stat.get('variable')
            statistic = dp_stat.get('statistic', 'shrug?')
            epsilon = dp_stat.get('epsilon')
            # Does the epsilon exceed the max epsilon?
            if epsilon > self.max_epsilon:
                self.add_stat_error(variable, statistic,
                                    f'{epsilon} exceeds max epsilon of {self.max_epsilon}')
                continue  # to the next dp_stat specification

            # (1) Variable is not in the spec
            #
            if not variable:
                user_msg = f'"variable" is missing from this DP Stat specification'
                self.add_stat_error(variable, statistic, user_msg)
                continue  # to the next dp_stat specification

            # (2) Is this a known statistic? If not stop here.
            #
            if not statistic in astatic.DP_STATS_CHOICES:  # also checked in the DPStatisticSerializer
                user_msg = f'Statistic "{statistic}" is not supported'
                self.add_stat_error(variable, statistic, user_msg)
                continue  # to the next dp_stat specification

            # (2) Begin building the property dict
            #
            props = dp_stat         # start with what is in dp_stat--the UI input
            props['impute_constant'] = dp_stat.get('fixed_value', None)   # one bit of renaming


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
                self.add_stat_error(variable, statistic, 'Variable info not found.')
                continue # to the next dp_stat specification


            # (4) Retrieve the column index
            #
            col_idx_info = self.analysis_plan.dataset.get_variable_index(variable)
            if col_idx_info.success:
                props['col_index'] = col_idx_info.data
            else:
                self.add_stat_error(variable, statistic, col_idx_info.message)
                continue  # to the next dp_stat specification


            # (5) Add the Dataset size
            #   - Logic here to see if dataset size should be added
            #
            dataset_size_info = self.analysis_plan.dataset.get_dataset_size()
            if not dataset_size_info.success:
                self.add_stat_error(variable, statistic, dataset_size_info.message)
                continue  # to the next dp_stat specification
            else:
                props['dataset_size'] = dataset_size_info.data

            # Okay, "props" are built! Let's see if they work!
            #
            if statistic == astatic.DP_MEAN:
                stat_spec = DPMeanSpec(props)
            elif statistic == astatic.DP_HISTOGRAM:
                user_msg = f'"{statistic}" will be supported soon! (hist)'
                self.add_stat_error(variable, statistic, user_msg)
                continue
            elif statistic in astatic.DP_STATS_CHOICES:
                user_msg = f'Statistic "{statistic}" will be supported soon!'
                self.add_stat_error(variable, statistic, user_msg)
                continue
            else:
                # Shouldn't reach here, unknown stats are captured up above
                pass

            if stat_spec.is_valid():
                running_epsilon += stat_spec.epsilon
                if running_epsilon > self.max_epsilon:
                    user_msg = (f'The running epsilon ({running_epsilon}) exceeds'
                                f' the max epsilon ({self.max_epsilon})')
                    self.add_stat_error(variable, statistic, user_msg)
                else:
                    self.validation_info.append(stat_spec.get_success_msg_dict())
            else:
                self.validation_info.append(stat_spec.get_error_msg_dict())

            continue  # to the next dp_stat specification!

            # -----------------------------------
            # original looping code below
            # -----------------------------------
            statistic = dp_stat['statistic']
            var_name = dp_stat['variable']  # User "variable", NOT "label"
            lower = upper = None

            # Is this a known statistic
            #
            if not statistic in astatic.DP_STATS_CHOICES:   # also checked in the DPStatisticSerializer
                user_msg = f'Statistic "{statistic}" is not supported'
                self.add_stat_error(var_name, statistic, user_msg)
                continue  # to the next dp_stat specification


            # Get the variable info
            #
            variable_info = self.analysis_plan.variable_info.get(var_name)
            if not variable_info:
                # Temp workaround!!! See Issue #300
                # https://github.com/opendp/dpcreator/issues/300
                variable_info = self.analysis_plan.variable_info.get(camel_to_snake(var_name))


            if not variable_info:
                self.add_stat_error(var_name, statistic, 'Variable info not found.')
                continue # to the next dp_stat specification



            if astatic.DP_STAT_NEED_MIN_MAX.get(statistic) is True:
                # Find the min/max in the variable info
                lower = variable_info.get('min')
                if lower is None:
                    self.add_stat_error(var_name, statistic, '"min" must be defined.')
                    continue # to the next dp_stat specification

                upper = variable_info.get('max')
                if upper is None:
                    self.add_stat_error(var_name, statistic, '"max" must be defined.')
                    continue # to the next dp_stat specification

            # Retrieve the column index
            #
            col_idx_info = self.analysis_plan.dataset.get_variable_index(var_name)
            if not col_idx_info.success:
                self.add_stat_error(var_name, statistic, col_idx_info.message)
                continue  # to the next dp_stat specification

            # get the column index
            col_idx = col_idx_info.data

            # Retrieve the dataset size
            #   -> Needs updating to related to DP questions!
            #
            dataset_size_info = self.analysis_plan.dataset.get_dataset_size()
            if not dataset_size_info.success:
                self.add_stat_error(var_name, statistic, dataset_size_info.message)
                continue  # to the next dp_stat specification
            dataset_size = dataset_size_info.data

            # Add missing value handling here...
            #   How to handle Missing Val!!!
            impute = dp_stat['missing_values_handling'] != astatic.MISSING_VAL_DROP
            impute_value = float(dp_stat['fixed_value'])

            # Validate epsilon
            epsilon = float(dp_stat['epsilon'])
            try:
                validate_epsilon_not_null(epsilon)
            except ValidationError as err_obj:
                self.add_stat_error(var_name, statistic, err_obj.message)
                continue  # to the next dp_stat specification!

            running_epsilon += epsilon
            if running_epsilon > self.max_epsilon:
                user_msg = (f'The running epsilon ({running_epsilon}) exceeds'
                            f' the max epsilon ({self.max_epsilon})')
                self.add_stat_error(var_name, statistic, user_msg)
                continue  # to the next dp_stat specification!

            # Do some validation and append to stats_valid
            if statistic == astatic.DP_MEAN:
                try:
                    # print(index, lower, upper, n, impute_value, dp_stat['epsilon'])
                    # print(list(map(type, (index, lower, upper, n, impute_value, dp_stat['epsilon']))))
                    _preprocessor = dp_mean(col_idx, lower, upper, dataset_size, impute_value, epsilon)

                    #
                    # TODO: add column index and statistic to result (maybe
                    self.validation_info.append(StatValidInfo.get_success_msg_dict(var_name, statistic))

                    continue  # to the next dp_stat specification
                except OpenDPException as ex_obj:
                    self.add_stat_error(var_name, statistic, ex_obj.message)
                    continue  # to the next dp_stat specification
                except Exception as ex_obj:
                    if hasattr(ex_obj, 'message'):
                        self.add_stat_error(var_name, statistic, ex_obj.message)
                    else:
                        self.add_stat_error(var_name, statistic, str(ex_obj))
                    continue  # to the next dp_stat specification

            elif statistic == astatic.DP_HISTOGRAM:
                user_msg = f'"{statistic}" will be supported soon! (hist)'
                self.add_stat_error(var_name, statistic, user_msg)
                continue  # to the next dp_stat specification

            elif statistic in astatic.DP_STATS_CHOICES:
                user_msg = f'Statistic "{statistic}" will be supported soon!'
                self.add_stat_error(var_name, statistic, user_msg)
                continue  # to the next dp_stat specification

            else:
                # Shouldn't reach here, unknown stats are captured up above
                pass

    def add_stat_error(self, var_name, statistic, user_msg):
        """
        Shortcut to add an error entry to self.validation_info
        """
        info = StatValidInfo.get_error_msg_dict(var_name, statistic, user_msg)
        self.validation_info.append(info)


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

        # Make sure the total epsilon is valid
        #
        self.max_epsilon = self.analysis_plan.dataset.get_depositor_setup_info().epsilon

        try:
            validate_epsilon_not_null(self.max_epsilon)
        except ValidationError as err_obj:
            user_msg = f'{astatic.ERR_MSG_BAD_TOTAL_EPSILON}: {self.max_epsilon}'
            self.add_err_msg(user_msg)
            return False

        return True

