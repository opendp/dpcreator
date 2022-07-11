"""
Used to create StatSpec objects including adding DPCount objects when necessary

"""
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
import pkg_resources
from typing import Union

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis.release_info_formatter import ReleaseInfoFormatter
from opendp_apps.analysis.tools.dp_variance_spec import DPVarianceSpec
from opendp_apps.analysis.release_email_util import ReleaseEmailUtil
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis.tools.dp_spec_error import DPSpecError
from opendp_apps.analysis.tools.dp_count_spec import DPCountSpec
from opendp_apps.analysis.tools.dp_histogram_integer_spec import DPHistogramIntegerSpec
from opendp_apps.analysis.tools.dp_histogram_categorical_spec import DPHistogramCategoricalSpec
from opendp_apps.analysis.tools.dp_mean_spec import DPMeanSpec
from opendp_apps.analysis.tools.dp_sum_spec import DPSumSpec

from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.dataverses.dataverse_deposit_util import DataverseDepositUtil

from opendp_apps.dp_reports.pdf_report_maker import PDFReportMaker

from opendp_apps.user.models import OpenDPUser
from opendp_apps.profiler import static_vals as pstatic

from opendp_apps.utils.extra_validators import \
    (validate_epsilon_not_null,
     validate_not_negative)
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.profiler.static_vals_mime_types import get_data_file_separator


logger = logging.getLogger(settings.DEFAULT_LOGGER)


class StatSpecBuilder(BasicErrCheck):

    def __init__(self, analysis_plan: AnalysisPlan, dp_statistics: list = None, **kwargs):
        """
        Note: Do not use the __init__ directly, use one of these static methods:
            - build_with_public_count(...)
            - build_with_private_count(...)
        """
        self.analysis_plan = analysis_plan
        self.dp_statistics = dp_statistics

        self.stat_spec_list = []
        self.stats_requiring_count = []
        self.dataset_size = None
        self.use_private_count = True   # May be changed during process via "determine_dataset_size()"
        self.dataset_size_required = True
        self.dp_count_added = False

        self.build_stat_specs()

    def add_err_msg(self, err_msg):
        """Add an error message"""
        self.error_found = True
        self.error_message = err_msg
        logger.error(err_msg)

    def run_build_stat_spec_process(self):
        """  """
        if self.has_error():
            return

        # Set the dp_statistics attribute
        if not self.set_dp_statistics():
            return

        # Determine the dataset size (if needed)
        if not self.determine_dataset_size():
            return

    def determine_dataset_size(self):
        """
        Depending on 'is_private_count" and the contents of `dp_statistics`,
        determine the dataset size
        """
        if self.has_error():
            return False

        # Make sure the AnalysisPlan plan object is there!
        if not self.analysis_plan:
            self.add_err_msg('The AnalysisPlan was not specified.')
            return False

        # If the dataset size isn't required, all set...
        self.dataset_size_required = self.is_dataset_size_required()
        if self.is_dataset_size_required() is False:
            return True

        # May the dataset size be made public?
        if self.analysis_plan.is_dataset_size_public():
            # Yes, use the actual dataset size
            self.dataset_size = self.analysis_plan.dataset.get_dataset_size()
            self.use_private_count = False
            return True

        # No, dataset size is not public
        self.use_private_count = True

        # Does the stats list already contain a count?
        if not self.does_stats_list_have_a_dp_count():
            # It there's no DP Count, then add one.
            self.add_dp_count()

        return True

    def is_dataset_size_required(self) -> bool:
        """Do any of the statistics require dataset_size for input?"""
        self.stats_requiring_count = []

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

    def add_dp_count(self):
        """Add a DP Count to the dp_statistics list"""
        if self.has_error():
            return

        if not self.stats_requiring_count:
            user_msg = "No stats found requiring a count"
            self.add_err_msg(user_msg)
            return False

        # For creating the count, use the first stat requiring a count
        #
        stat_needing_count = self.stats_requiring_count[0]

        dp_count = {
            astatic.KEY_AUTO_GENERATED_DP_COUNT: True,
            "statistic": astatic.DP_COUNT,
            "variable": stat_needing_count['variable'],
            "label": stat_needing_count['variable'],
            "epsilon": 0.1, # TODO: FIX! (initial test value)
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

    def compute_dp_count_for_validation(self):
        """
        Naive version, use the first DP Count in list
        - Return None or integer count
        """
        if self.has_error():
            return None

        # Get the DP Count specification
        dp_count_spec = self.get_first_dp_count_spec()
        if dp_count_spec is None:
            return None

        # Add variable info and column index
        dp_count_spec = self.set_stat_spec_additional_params(dp_count_spec)
        if dp_count_spec is None:
            return None

        if 'error_message' in dp_count_spec:
            self.add_err_msg(dp_count_spec['error_message'])
            return None

        # Is the spec valid
        if dp_count_spec.has_error():
            user_msg = (f'Validation error found for variable "{dp_count_spec.variable}"'
                        f' and statistic "{dp_count_spec.statistic}":'
                        f' {dp_count_spec.get_single_err_msg()}')
            self.add_err_msg(user_msg)
            return

        #
        variable_indices_info = self.analysis_plan.dataset.get_variable_order(as_indices=True)
        if not variable_indices_info.success:
            user_msg = f'Failed to get column indices. {variable_indices_info.message}'
            self.add_err_msg(user_msg)
            return None

        col_indices = variable_indices_info.data

        # -----------------------------------
        # Get the file/dataset pointer -- needs adjusting for blob/S3 type objects
        # -----------------------------------
        try:
            filepath = self.analysis_plan.dataset.source_file.path
        except ValueError as err_obj:
            user_msg = (f'Failed to calculate statistics. Unable to access the data file. '
                        f' ({err_obj})')
            self.add_err_msg(user_msg)
            return

        sep_char = get_data_file_separator(filepath)

        file_handle = open(filepath, 'r')
        stat_spec.run_chain(col_indices, file_handle, sep_char=sep_char)
        file_handle.close()

    def set_stat_spec_additional_params(self, stat_spec: dict) -> dict:
        """For an initial stat spec from dp_statistics, add 'variable_info' and the 'col_idx'"""
        if self.has_error():
            return None

        if not stat_spec:
            user_msg = '"stat_spec" cannot be unspecified.'
            self.add_err_msg(user_msg)
            return None

        var_name = stat_spec.get('variable')
        variable_info = self.analysis_plan.variable_info.get(var_name)
        if not variable_info:
            user_msg = f'Variable info for {var_name} not found.'
            stat_spec['error_message'] = user_msg
            # self.add_err_msg(user_msg)
            return stat_spec
        else:
            stat_spec['variable_info'] = variable_info

        col_idx_info = self.analysis_plan.dataset.get_variable_index(variable_info.get('name'))
        if col_idx_info.success:
            stat_spec['col_index'] = col_idx_info.data
        else:
            stat_spec['error_message'] = col_idx_info.message

        return stat_spec

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
            stat_num += 1       # not used yet...
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
            props = dp_stat         # start with what is in dp_stat--the UI input
            props['dataset_size'] = self.dataset_size   # add dataset size

            #  Some high-level error checks, before making the StatSpec
            variable = props.get('variable')
            statistic = props.get('statistic', 'shrug?')
            # epsilon = props.get('epsilon')
            # var_type = None

            # (1) Is variable defined?
            if not props.get('variable'):
                props['error_message'] = (f'"variable" is missing from this'
                                          f'DP Stat specification.')
                self.add_stat_spec(DPSpecError(props))
                continue  # to the next dp_stat specification

            # (2) Is this a known statistic? If not stop here.
            if statistic not in astatic.DP_STATS_CHOICES:
                props['error_message'] = f'Statistic "{statistic}" is not supported'
                self.add_stat_spec(DPSpecError(props))
                logger.error(f'ValidateReleaseUtil.build_stat_specs: Statistic "{statistic}" is not supported')
                continue  # to the next dp_stat specification

            # (3) Add variable_info which has min/max/categories, variable type, etc.
            variable_info = self.analysis_plan.variable_info.get(variable)
            if variable_info:
                props['variable_info'] = variable_info
                var_type = variable_info.get('type')
            else:
                props['error_message'] = 'Variable in validation info not found.'
                self.add_stat_spec(DPSpecError(props))
                logger.error(f'ValidateReleaseUtil.build_stat_specs: Variable in validation info not found.')
                continue  # to the next dp_stat specification

            # (4) Retrieve the column index
            col_idx_info = self.analysis_plan.dataset.get_variable_index(variable_info['name'])
            if col_idx_info.success:
                props['col_index'] = col_idx_info.data
            else:
                props['error_message'] = col_idx_info.message
                self.add_stat_spec(DPSpecError(props))
                logger.error(f'ValidateReleaseUtil.build_stat_specs: {col_idx_info.message}')
                continue  # to the next dp_stat specification

            # Okay, "props" are built! Let's see if they work!
            if statistic == astatic.DP_COUNT:
                # DP Count!
                self.add_stat_spec(DPCountSpec(props))

            elif statistic in astatic.DP_HISTOGRAM:
                if var_type == pstatic.VAR_TYPE_CATEGORICAL:
                    # 4/12/2022 - temp hack to distinguish numeric categories
                    #   - need updated UI, etc.
                    #
                    has_int_cats, _min_max = self.has_integer_categories(props)

                    if has_int_cats:
                        # Artificially set the min/max
                        #
                        props['variable_info']['type'] = pstatic.VAR_TYPE_INTEGER
                        props['variable_info']['min'] = _min_max[0]
                        props['variable_info']['max'] = _min_max[1]
                        self.add_stat_spec(DPHistogramIntegerSpec(props))
                    else:
                        self.add_stat_spec(DPHistogramCategoricalSpec(props))

                elif var_type == pstatic.VAR_TYPE_INTEGER:
                    # DP Histogram (Integer)!
                    self.add_stat_spec(DPHistogramIntegerSpec(props))

                else:
                    # DP Histogram - unsupported type
                    props['error_message'] = (f'Statistic is "{astatic.DP_HISTOGRAM}" but '
                                              f' variable type is unsupported: "{var_type}"')
                    self.add_stat_spec(DPSpecError(props))
                    logger.error(f'ValidateReleaseUtil.build_stat_specs: Statistic is "{astatic.DP_HISTOGRAM}" but '
                                 f'variable type is unsupported: "{var_type}"')
                    continue  # to the next dp_stat specification

            elif statistic == astatic.DP_MEAN:
                # DP Mean!
                self.add_stat_spec(DPMeanSpec(props))

            elif statistic == astatic.DP_SUM:
                # DP Mean!
                self.add_stat_spec(DPSumSpec(props))

            elif statistic == astatic.DP_VARIANCE:
                self.add_stat_spec(DPVarianceSpec(props))

            elif statistic in astatic.DP_STATS_CHOICES:
                # Stat not yet available or an error
                props['error_message'] = (f'Statistic "{statistic}" will be supported'
                                          f' soon!')
                logger.error('ValidateReleaseUtil.build_stat_specs: Statistic "{statistic}" will be supported soon!')
                self.add_stat_spec(DPSpecError(props))
            else:
                # Shouldn't reach here, unknown stats are captured up above
                pass
