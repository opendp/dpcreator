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
import copy
import logging
from typing import Union

from django.conf import settings

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.models import AnalysisPlan
from opendp_apps.analysis.tools.dp_count_spec import DPCountSpec
from opendp_apps.analysis.tools.dp_histogram_categorical_spec import DPHistogramCategoricalSpec
from opendp_apps.analysis.tools.dp_histogram_integer_spec import DPHistogramIntegerSpec
from opendp_apps.analysis.tools.dp_mean_spec import DPMeanSpec
from opendp_apps.analysis.tools.dp_spec_error import DPSpecError
from opendp_apps.analysis.tools.dp_sum_spec import DPSumSpec
from opendp_apps.analysis.tools.dp_variance_spec import DPVarianceSpec
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.profiler import static_vals as pstatic

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class StatSpecBuilder(BasicErrCheck):

    def __init__(self, analysis_plan: AnalysisPlan, dp_statistics: list = None):
        """
        Note: Do not use the __init__ directly, use one of these static methods:
            - build_with_public_count(...)
            - build_with_private_count(...)
        """
        self.analysis_plan = analysis_plan
        self.dp_statistics = dp_statistics

        self.max_epsilon = None  # retrieved later via the analysis_plan
        self.stat_spec_list = []
        self.stats_requiring_count = []

        self.validation_dataset_size = None  # Dataset size from profile; used for validation
        self.use_private_count = True  # Conservative default; May change via "determine_dataset_size()"
        self.dataset_size_required = True
        self.dp_count_added = False

        self.run_build_spec_process()

    def add_err_msg(self, err_msg):
        """Add an error message"""
        self.error_found = True
        self.error_message = err_msg
        logger.error(err_msg)

    def get_stat_spec_list(self) -> list:
        """Return a list of StatSpec objects"""
        assert self.has_error() is False, 'Verify that "has_error()" is False before calling this method'

        return self.stat_spec_list

    def run_build_spec_process(self):
        """Build/validate the stat specs  """
        if self.has_error():
            return

        if not self.set_max_epsilon():
            return

        # Set the dp_statistics attribute
        if not self.set_dp_statistics():
            return

        # Determine the dataset size (if needed)
        if not self.determine_dataset_size():
            return

        # Build StatSpec list
        self.build_stat_specs()

    def set_max_epsilon(self) -> bool:
        """Set the max epsilon based on the analysis plan"""
        if not self.analysis_plan:
            self.add_err_msg('The AnalysisPlan was not specified.')
            return False

        self.max_epsilon = self.analysis_plan.dataset.get_depositor_setup_info().epsilon

        return True

    def determine_dataset_size(self):
        """
        Depending on 'is_private_count" and the contents of `dp_statistics`,
        determine the dataset size.

        """
        if self.has_error():
            return False

        # Make sure the AnalysisPlan plan object is there!
        if not self.analysis_plan:
            self.add_err_msg('The AnalysisPlan was not specified.')
            return False

        # Use the actual dataset size FOR VALIDATION ONLY
        #
        ds_size_info = self.analysis_plan.dataset.get_dataset_size()
        if not ds_size_info.success:
            self.add_err_msg(ds_size_info.message)
            return False

        self.validation_dataset_size = ds_size_info.data

        # If the dataset size isn't required, all set...
        #
        self.dataset_size_required = self.is_dataset_size_required()
        if not self.is_dataset_size_required():
            return True

        # May the dataset size be made public?
        if self.analysis_plan.is_dataset_size_public():
            self.use_private_count = False
        else:
            # No, dataset size is not public
            self.use_private_count = True

        # If the count must be private, does the stats list already contain a count?
        if self.use_private_count is True and not self.does_stats_list_have_a_dp_count():
            # It there's no DP Count, then add one.
            self.add_dp_count()
            success, dp_stats_or_err = self.redistribute_epsilon(self.max_epsilon, self.dp_statistics)
            if success is True:
                self.dp_statistics = dp_stats_or_err
            else:
                self.add_err_msg(dp_stats_or_err)
                return False

        return True

    def is_dataset_size_required(self) -> bool:
        """Do any of the statistics require dataset_size for input?"""
        self.stats_requiring_count = []

        # Iterate through the statistics
        # For those requiring dataset size, add them to a list
        #
        for dp_stat in self.dp_statistics:
            stat_name = dp_stat.get('statistic', None)
            if not self.is_valid_statistic_name(stat_name):
                return False

            # save the stats requiring a count
            if stat_name in astatic.DP_STATS_REQUIRE_COUNTS:
                self.stats_requiring_count.append(dp_stat)

        if self.stats_requiring_count:
            return True

        return False

    @staticmethod
    def redistribute_epsilon(max_epsilon, dp_statistics) -> tuple:
        """
        Redistribute the epsilon between stats **after** adding a new DP Count
        """
        # How many locked vs unlocked stats?
        #
        num_locked_stats = len([dp_stat for dp_stat in dp_statistics
                                if dp_stat.get('locked') is True])
        num_unlocked_stats = len(dp_statistics) - num_locked_stats

        # How much epsilon is locked? e.g. can't be redistributed
        #
        locked_epsilon = 0
        if num_locked_stats > 0:
            locked_epsilon = sum([dp_stat['epsilon'] for dp_stat in dp_statistics
                                  if dp_stat.get('locked') is True])

        if locked_epsilon >= max_epsilon:
            return False, astatic.ERR_MSG_BAD_TOTAL_LOCKED_EPSILON

        # Set new epsilon for each unlocked stat
        #
        new_unlocked_epsilon = ((max_epsilon - locked_epsilon) / num_unlocked_stats) - astatic.MAX_EPSILON_OFFSET

        updated_stats = []
        for dp_stat in dp_statistics:
            if dp_stat.get('locked') is False:
                dp_stat['epsilon'] = new_unlocked_epsilon
            updated_stats.append(dp_stat)

        return True, updated_stats

    def add_dp_count(self):
        """Add a DP Count to the dp_statistics list"""
        if self.has_error():
            return False

        if not self.stats_requiring_count:
            user_msg = "No stats found requiring a count"
            self.add_err_msg(user_msg)
            return False

        # For creating the count, use the first stat requiring a count
        #
        stat_needing_count = self.stats_requiring_count[0]

        dp_count = {
            astatic.KEY_AUTO_GENERATED: True,
            "statistic": astatic.DP_COUNT,
            "variable": stat_needing_count['variable'],
            "label": stat_needing_count['variable'],
            "epsilon": 0.1,  # This will be set/redistributed!
            "delta": 0,
            astatic.KEY_MISSING_VALUES_HANDLING: stat_needing_count[astatic.KEY_MISSING_VALUES_HANDLING],
            astatic.KEY_FIXED_VALUE: stat_needing_count["fixed_value"],
            "handle_as_fixed": True,
            "locked": False,
        }

        # add to the top of the stats list
        self.dp_statistics.insert(0, dp_count)
        self.dp_count_added = True

        return True

    def is_valid_statistic_name(self, stat_name) -> bool:
        """Check if the statistic name is valid"""
        if stat_name in astatic.DP_STATS_CHOICES:
            return True

        if not stat_name:
            user_msg = (f'The "statistic" was not included in the DP stat specification.'
                        f' Valid choices: {astatic.VALID_DP_STATS_CHOICES_STR}')
        else:
            user_msg = (f'The "statistic, "{stat_name}", is unknown.'
                        f' Valid choices: {astatic.VALID_DP_STATS_CHOICES_STR}')

        self.add_err_msg(user_msg)

        return False

    def get_first_dp_count_spec(self) -> Union[dict, None]:
        """From the dp_statistics list, return the first DPCount spec or None"""
        for dp_stat in self.dp_statistics:
            stat_name = dp_stat.get('statistic', None)
            if not stat_name:
                user_msg = 'The "statistic" was not included in the DP stat specification.'
                self.add_err_msg(user_msg)
                return None

            if stat_name == astatic.DP_COUNT:
                return dp_stat

        return None

    def does_stats_list_have_a_dp_count(self) -> bool:
        """Does the stats list already have a DP Count?"""
        if self.get_first_dp_count_spec() is None:
            return False

        return True

    def set_dp_statistics(self) -> bool:
        """Are their dp_statistics in __init__ or in the analysis_plan"""

        # (1) Were dp_statistics explicitly set?
        if self.dp_statistics:
            return True

        # (2) Nope,  Does the AnalysisPlan have dp_statistics?
        if self.analysis_plan.dp_statistics:
            self.dp_statistics = self.analysis_plan.dp_statistics
            return True

        # (3) Nothing set...
        user_msg = 'The "dp_statistics" were not set and could not be found in the AnalysisPlan'
        self.add_err_msg(user_msg)
        return False

    def add_stat_spec(self, stat_spec: StatSpec):
        """Add a StatSpec subclass to a list"""
        self.stat_spec_list.append(stat_spec)

    def build_stat_specs(self):
        """
        Build a list of StatSpec subclasses that can be used for
        chain validation or running computations
        """
        if self.has_error():
            return

        # Iterate through the stats!
        self.stat_spec_list = []
        stat_num = 0

        for dp_stat in self.dp_statistics:
            stat_num += 1  # not used yet...
            """
            We're putting together lots of properties to pass to
            statistic specific classes such as DPMeanSpec.

            These classes take care of most error checking and validation.

            - Some sample input from the UI--e.g. contents of "dp_stat:
                {
                    "statistic": astatic.DP_MEAN,
                    "variable_key": "eye_height"
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
            dp_stat['dataset_size'] = self.validation_dataset_size  # add dataset size

            #  Some high-level error checks, before making the StatSpec
            variable = dp_stat.get('variable')
            statistic = dp_stat.get('statistic', 'shrug?')
            # epsilon = dp_stat.get('epsilon')
            # var_type = None

            # (1) Is variable defined?
            if not dp_stat.get('variable'):
                dp_stat['error_message'] = (f'The "variable" is missing from this'
                                            f'DP Stat specification.')
                self.add_stat_spec(DPSpecError(dp_stat))
                continue  # to the next dp_stat specification

            # (2) Is this a known statistic? If not stop here.
            if statistic not in astatic.DP_STATS_CHOICES:
                dp_stat['error_message'] = f'Statistic "{statistic}" is not supported'
                self.add_stat_spec(DPSpecError(dp_stat))
                logger.error(f'ValidateReleaseUtil.build_stat_specs: Statistic "{statistic}" is not supported')
                continue  # to the next dp_stat specification

            # (3) Add variable_info which has min/max/categories, variable type, etc.
            variable_info = self.analysis_plan.variable_info.get(variable)
            if variable_info:
                dp_stat['variable_info'] = variable_info
                var_type = variable_info.get('type')
            else:
                dp_stat['error_message'] = 'Variable in validation info not found.'
                self.add_stat_spec(DPSpecError(dp_stat))
                logger.error(f'ValidateReleaseUtil.build_stat_specs: Variable in validation info not found.')
                continue  # to the next dp_stat specification

            # (4) Retrieve the column index
            col_idx_info = self.analysis_plan.dataset.get_variable_index(variable_info['name'])
            if col_idx_info.success:
                dp_stat['col_index'] = col_idx_info.data
            else:
                dp_stat['error_message'] = col_idx_info.message
                self.add_stat_spec(DPSpecError(dp_stat))
                logger.error(f'ValidateReleaseUtil.build_stat_specs: {col_idx_info.message}')
                continue  # to the next dp_stat specification

            # Okay, "dp_stat" are built! Let's see if they work!
            if statistic == astatic.DP_COUNT:
                # DP Count!
                self.add_stat_spec(DPCountSpec(dp_stat))

            elif statistic in astatic.DP_HISTOGRAM:
                if var_type == pstatic.VAR_TYPE_CATEGORICAL:
                    # 4/12/2022 - temp hack to distinguish numeric categories
                    #   - need updated UI, etc.
                    #
                    has_int_cats, _min_max = self.has_integer_categories(dp_stat)

                    if has_int_cats:
                        # Artificially set the min/max
                        #
                        dp_stat['variable_info']['type'] = pstatic.VAR_TYPE_INTEGER
                        dp_stat['variable_info']['min'] = _min_max[0]
                        dp_stat['variable_info']['max'] = _min_max[1]
                        self.add_stat_spec(DPHistogramIntegerSpec(dp_stat))
                    else:
                        self.add_stat_spec(DPHistogramCategoricalSpec(dp_stat))

                elif var_type == pstatic.VAR_TYPE_INTEGER:
                    # DP Histogram (Integer)!
                    self.add_stat_spec(DPHistogramIntegerSpec(dp_stat))

                else:
                    # DP Histogram - unsupported type
                    dp_stat['error_message'] = (f'Statistic is "{astatic.DP_HISTOGRAM}" but '
                                                f' variable type is unsupported: "{var_type}"')
                    self.add_stat_spec(DPSpecError(dp_stat))
                    logger.error(f'ValidateReleaseUtil.build_stat_specs: Statistic is "{astatic.DP_HISTOGRAM}" but '
                                 f'variable type is unsupported: "{var_type}"')
                    continue  # to the next dp_stat specification

            elif statistic == astatic.DP_MEAN:
                # DP Mean!
                self.add_stat_spec(DPMeanSpec(dp_stat))

            elif statistic == astatic.DP_SUM:
                # DP Mean!
                self.add_stat_spec(DPSumSpec(dp_stat))

            elif statistic == astatic.DP_VARIANCE:
                self.add_stat_spec(DPVarianceSpec(dp_stat))

            elif statistic in astatic.DP_STATS_CHOICES:
                # Stat not yet available or an error
                dp_stat['error_message'] = (f'Statistic "{statistic}" will be supported'
                                            f' soon!')
                logger.error('ValidateReleaseUtil.build_stat_specs: Statistic "{statistic}" will be supported soon!')
                self.add_stat_spec(DPSpecError(dp_stat))
            else:
                # Shouldn't reach here, unknown stats are captured up above
                pass

    @staticmethod
    def has_integer_categories(dp_stat: dict):
        """
        # 4/12/2022 - temporary hack for histograms
        Check if the dp_stat['variable_info']['categories'] list consists of continuous integers

        False: return False, None
        True:  return True, (min, max)
        """
        if not dp_stat:
            return False, None

        # Are there categories?
        if ('variable_info' in dp_stat) and ('categories' in dp_stat['variable_info']):

            # Get the categories
            cats = copy.deepcopy(dp_stat['variable_info']['categories'])

            # Are all the values integers?
            all_int_check = [isinstance(x, int) for x in cats]

            # Nope, return
            if False in all_int_check:
                return False, None

            # All integers, are they continuous?
            if sorted(cats) == list(range(min(cats), max(cats) + 1)):
                return True, (min(cats), max(cats))

        return False, None
