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
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.models import AnalysisPlan, ReleaseInfo
from opendp_apps.analysis.release_email_util import ReleaseEmailUtil
from opendp_apps.analysis.release_info_formatter import ReleaseInfoFormatter
from opendp_apps.analysis.tools.dp_count_spec import DPCountSpec
from opendp_apps.analysis.tools.dp_mean_spec import DPMeanSpec
from opendp_apps.analysis.tools.dp_spec_error import DPSpecError
from opendp_apps.analysis.tools.dp_sum_spec import DPSumSpec
from opendp_apps.analysis.tools.dp_variance_spec import DPVarianceSpec
from opendp_apps.analysis.tools.histogram_util import get_histogram_stat_spec
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.dataset.models import DatasetInfo
# from opendp_apps.dataverses.dataverse_deposit_util import DataverseDepositUtil
from opendp_apps.dp_reports.pdf_report_maker import PDFReportMaker
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.profiler.static_vals_mime_types import get_data_file_separator
from opendp_apps.user.models import OpenDPUser
from opendp_apps.utils.extra_validators import \
    (validate_epsilon_not_null,
     validate_not_negative)

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class ValidateReleaseUtil(BasicErrCheck):

    def __init__(self, opendp_user: OpenDPUser, analysis_plan_id: int,
                 dp_statistics: list = None, compute_mode: bool = False, **kwargs):
        """
        In most cases, don't use this method directly.
        To initialize, use:
            - ValidateReleaseUtil.validate_mode(...)  # e.g. run validations only
            - ValidateReleaseUtil.compute_mode(...)     # run the commputation chain
        """
        self.opendp_user = opendp_user  # to be retrieved

        self.analysis_plan_id = analysis_plan_id
        self.analysis_plan = None  # to be retrieved

        self.dp_statistics = dp_statistics  # User defined
        self.compute_mode = compute_mode

        self.run_dataverse_deposit = kwargs.get('run_dataverse_deposit', False)

        self.max_epsilon = None  # from analysis_plan.dataset.get_depositor_setup_info()
        self.max_delta = None  # from analysis_plan.dataset.get_depositor_setup_info()
        self.dataset_size = None  # from analysis_plan.dataset

        self.stat_spec_list = []  # list of StatSpec objects
        self.validation_info = []  # list of StatValidInfo objects to send to UI

        self.release_stats = []  # compute mode: potential stat for a ReleaseInfo
        self.release_info = None  # compute_mode: potential full ReleaseInfo object

        self.opendp_version = pkg_resources.get_distribution('opendp').version

        if self.compute_mode is True:
            self.run_release_process()
        else:
            self.run_validation_process()

    @staticmethod
    def validate_mode(opendp_user: OpenDPUser, analysis_plan_id: int,
                      dp_statistics: list = None):
        """
        Use this method to return a ValidateReleaseUtil validates the dp_statistics
        """
        return ValidateReleaseUtil(opendp_user, analysis_plan_id, dp_statistics)

    @staticmethod
    def compute_mode(opendp_user: OpenDPUser, analysis_plan_id: int,
                     run_dataverse_deposit: bool = False):
        """
        Use this method to return a ValidateReleaseUtil which runs the dp_statistics
        """
        return ValidateReleaseUtil(opendp_user,
                                   analysis_plan_id,
                                   dp_statistics=None,
                                   compute_mode=True,
                                   **dict(run_dataverse_deposit=run_dataverse_deposit))

    def add_stat_spec(self, stat_spec: StatSpec):
        """Add a StatSpec subclass to a list"""
        assert isinstance(stat_spec, StatSpec), \
            "stat_spec must be an instance of StatSpec"
        self.stat_spec_list.append(stat_spec)

    def run_release_process(self):
        """
        Run the release process which includes:
        - validation of the analysis plan
        - running the computation chain for each statistic
        - create a ReleaseInfo object
            - create/add a JSON file
            - create/add a PDF file
        - deposit the files to Dataverse (if appropriate)
        """
        if self.has_error():
            return

        # -----------------------------------
        # Validate again!! Just in case!!
        # -----------------------------------
        self.run_validation_process()

        # Any general validation errors?
        if self.has_error():
            return

        # Any stat specific validation errors?
        #   - Fail on 1st error found
        for stat_spec in self.stat_spec_list:
            if stat_spec.has_error():
                stat_spec.print_debug()
            if stat_spec.has_error():
                user_msg = (f'Validation error found for variable "{stat_spec.variable}"'
                            f' and statistic "{stat_spec.statistic}":'
                            f' {stat_spec.get_single_err_msg()}')
                self.add_err_msg(user_msg)
                return

        # -----------------------------------
        # Get the column indices--necessary for "run_chain(...)"
        # -----------------------------------
        col_indices = self.get_variable_indices()
        if col_indices is None:
            return

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

        # -----------------------------------
        # Iterate through the stats!
        # -----------------------------------
        self.release_stats = []
        epsilon_used = 0.0
        for stat_spec in self.stat_spec_list:

            # Okay! -> run_chain(...)!
            file_handle = open(filepath, 'r')
            stat_spec.run_chain(col_indices, file_handle, sep_char=sep_char)
            file_handle.close()

            # Any errors?
            if not stat_spec.has_error():
                # Looks good! Save the stat
                self.release_stats.append(stat_spec.get_release_dict())
                epsilon_used += stat_spec.epsilon
            else:
                user_msg = (f'Validation error found for {stat_spec.statistic}:'
                            f' {stat_spec.get_single_err_msg()}')
                logger.error(f'Validation error found for {stat_spec.statistic}:'
                             f' {stat_spec.get_single_err_msg()}')
                self.add_err_msg(user_msg)
                # Delete any previous stats
                del self.release_stats
                return

        # should never happen!
        if not self.release_stats:
            user_msg = ("ValidateReleaseUtil.run_release_process.'"
                        "No release_stats! shouldn't see this error!")
            logger.error("ValidateReleaseUtil.run_release_process.'"
                         "No release_stats! shouldn't see this error!")
            self.add_err_msg(user_msg)
            return

        # It worked! Save the Release!!
        self.make_release_info(epsilon_used)

        # Deposit release files in Dataverse
        if not self.has_error():
            self.deposit_to_dataverse()

    def deposit_to_dataverse(self):
        """
        Using the ReleaseInfo object, deposit any release files to Dataverse
        """
        if self.has_error():
            return

        if not self.analysis_plan.dataset.is_dataverse_dataset():
            # Not needed for this ReleaseInfo
            return

        if not self.run_dataverse_deposit:
            return

        if not self.release_info:
            # Shouldn't happen!
            logger.error('ValidateReleaseUtil.deposit_to_dataverse: ReleaseInfo not available for Dataverse deposit')
            self.add_err_msg('ReleaseInfo not available for Dataverse deposit')

        self.analysis_plan.user_step = AnalysisPlan.AnalystSteps.STEP_1200_PROCESS_COMPLETE
        self.analysis_plan.save()
        logger.info('ValidateReleaseUtil: Deposit complete!')

        # If the ReleaseInfo object was crated and deposit fails,
        # the error for the deposit will be sent to the user
        # deposit_util = DataverseDepositUtil(self.release_info)
        # if deposit_util.has_error():
        #    logger.error(deposit_util.get_err_msg())
        #    return

    def make_release_info(self, epsilon_used: float):
        """
        Make a ReleaseInfo object!
        """
        assert epsilon_used > 0.0, "make_release_info/ Something's wrong! Epsilon should always be > 0"
        self.release_info = None

        # (1) Format the release JSON as a Python dict as well as JSON string
        formatted_release = self.get_final_release_data()
        if self.has_error():
            del self.release_stats
            return False

        # (2)
        formatted_release_json_str = self.get_final_release_data(as_json=True)
        if self.has_error():
            del self.release_stats
            return False

        # (3) Save the ReleaseInfo object
        params = dict(dataset=self.analysis_plan.dataset,
                      epsilon_used=epsilon_used,
                      dp_release=formatted_release)

        self.release_info = ReleaseInfo(**params)
        self.release_info.save()

        # (4) Save Release JSON string to a file on field ReleaseInfo.dp_release_json
        #
        json_filename = ReleaseInfoFormatter.get_json_filename(self.release_info)

        django_file = ContentFile(formatted_release_json_str.encode())
        self.release_info.dp_release_json_file.save(json_filename, django_file)
        self.release_info.save()

        # -------------------------------
        # (4a) Save Release PDF
        # -------------------------------
        # Make Async! create the release PDF
        # -------------------------------
        logger.info(f'SKIP_PDF_CREATION_FOR_TESTS: {settings.SKIP_PDF_CREATION_FOR_TESTS}')
        if settings.SKIP_PDF_CREATION_FOR_TESTS:
            # Skip PDF creation during tests to save time
            pass
        else:
            report_maker = PDFReportMaker(self.release_info.dp_release, self.release_info.object_id)
            if not report_maker.has_error():
                report_maker.save_pdf_to_release_obj(self.release_info)

        # (5) Attach the ReleaseInfo to the AnalysisPlan, AnalysisPlan.release_info
        self.analysis_plan.release_info = self.release_info
        self.analysis_plan.user_step = AnalysisPlan.AnalystSteps.STEP_1000_RELEASE_COMPLETE
        self.analysis_plan.save()

        # (6) Delete the "source_file"
        delete_result = DatasetInfo.delete_source_file(self.analysis_plan.dataset)
        if not delete_result.success:
            logger.error(f"ValidateReleaseUtil.make_release_info: {delete_result.message}")
            self.add_err_msg(delete_result.message)
            return False

        # (7) Send release email to the user
        #   (On error, continue the process)
        if settings.SKIP_EMAIL_RELEASE_FOR_TESTS:
            pass
        else:
            _email_util = ReleaseEmailUtil(self.release_info)

        return True

    def get_new_release_info_object(self):
        assert self.has_error() is False, \
            "Check that .has_error() is False before calling this method"

        return self.release_info

    def get_final_release_data(self, as_json=False):
        """Build object to save in ReleaseInfo.dp_release"""
        formatter = ReleaseInfoFormatter(self)

        if formatter.has_error():
            # shouldn't happen, but over time...
            logger.error(f'ValidateReleaseUtil.get_final_release_data: {formatter.get_err_msg()}')
            self.add_err_msg(formatter.get_err_msg())
            return

        rd = formatter.get_release_data(as_json=as_json)

        return rd

    def get_release_stats(self):
        """Return the release stats"""
        assert self.has_error() is False, \
            "Check that .has_error() is False before calling this method"

        return self.release_stats

    def run_validation_process(self):
        """Run the validation"""
        if not self.run_preliminary_steps():
            return

        # Make sure the variable indices are available!
        # Not needed in this step but required for computation
        if self.get_variable_indices() is None:
            # error set in ^ get_variable_indices()
            return

        self.build_stat_specs()

        #print('\n\n>>> stat_spec_list', self.stat_spec_list)
        #for x in self.stat_spec_list:
        #    if x.has_error():
        #        print(x, x.get_single_err_msg())

        if not self.stat_spec_list:
            logger.error('ValidateReleaseUtil.run_validation_process: No statistics were built!')
            self.add_err_msg('No statistics were built!')
            return

        # Iterate through the stat specs and validate them!
        #
        self.validation_info = []  # reset validation info
        running_epsilon = 0.0
        item_cnt = 0
        for stat_spec in self.stat_spec_list:
            item_cnt += 1
            # Check each stat_spec
            if not stat_spec.is_chain_valid():
                # Nope: invalid!
                self.validation_info.append(stat_spec.get_error_msg_dict())
            else:
                # Looks good but check single stat epsilon and cumulative epsilon
                running_epsilon += stat_spec.epsilon

                if stat_spec.epsilon > self.max_epsilon:
                    # Error one stat uses more than all the epsilon!
                    user_msg = (f'The epsilon ({stat_spec.epsilon}) exceeds'
                                f' max epsilon ({self.max_epsilon})')
                    stat_spec.add_err_msg(user_msg)
                    logger.error(f'ValidateReleaseUtil.run_validation_process: {user_msg}')
                    self.validation_info.append(stat_spec.get_error_msg_dict())

                elif (running_epsilon - astatic.MAX_EPSILON_OFFSET) > self.max_epsilon:
                    # Error: Too much epsilon used!
                    user_msg = (f'The running epsilon ({running_epsilon}) exceeds'
                                f' the max epsilon ({self.max_epsilon})')
                    stat_spec.add_err_msg(user_msg)
                    logger.error(f'ValidateReleaseUtil.run_validation_process: {user_msg}')
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
        logger.error(f'ValidateReleaseUtil.get_variable_indices: {variable_indices_info.message}')
        self.add_err_msg(variable_indices_info.message)
        return None

    def build_stat_specs(self):
        """
        Build a list of StatSpec subclasses that can be used for
        chain validation or running computations
        """
        # Iterate through the stats!
        self.stat_spec_list = []
        stat_num = 0
        for dp_stat in self.dp_statistics:
            stat_num += 1  # not used yet...
            print(f'\n\n20 (b-{stat_num})', dict(dp_stat))
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
            props = copy.deepcopy(dp_stat)  # start with what is in dp_stat--the UI input
            props['dataset_size'] = self.dataset_size  # add dataset size

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
                print('>>make statSpec: variable_info', variable_info)
                var_type = variable_info.get('type')
                props['var_type'] = var_type
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
                # DP Histogram
                # - Use function from HistogramUtil to determine correct StatSpec
                #
                hist_stat_spec = get_histogram_stat_spec(props)
                self.add_stat_spec(hist_stat_spec)

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
                logger.error(('ValidateReleaseUtil.build_stat_specs: Statistic'
                              ' "{statistic}" will be supported soon!'))
                self.add_stat_spec(DPSpecError(props))
            else:
                logger.error(('ValidateReleaseUtil.build_stat_specs: Shouldn\'t reach'
                              ' here, unknown stats are captured up above'))
                # Shouldn't reach here, unknown stats are captured up above
                pass

    def run_preliminary_steps(self):
        """Run preliminary steps before validation"""

        # Retrieve the Analysis Plan
        ap_info = AnalysisPlanUtil.retrieve_analysis(self.analysis_plan_id, self.opendp_user)
        if not ap_info.success:
            self.add_err_msg(ap_info.message)
            logger.error(f'ValidateReleaseUtil.run_preliminary_steps: {ap_info.message}')
            return False

        self.analysis_plan = ap_info.data

        # Check the dp_statistics spec
        if self.compute_mode:
            # In compute mode, run the stats saved in the plan!
            self.dp_statistics = self.analysis_plan.dp_statistics
            if not self.dp_statistics:
                user_msg = 'The AnalysisPlan does not contain "dp_statistics"'
                self.add_err_msg(user_msg)
                logger.error(f'ValidateReleaseUtil.run_preliminary_steps: {user_msg}')
                return False
        elif not self.dp_statistics:
            user_msg = 'There are no statistics to validate'
            self.add_err_msg(user_msg)
            logger.error(f'ValidateReleaseUtil.run_preliminary_steps: {user_msg}')
            return False

        dataset_size_info = self.analysis_plan.dataset.get_dataset_size()
        if dataset_size_info.success:
            self.dataset_size = dataset_size_info.data
        else:
            user_msg = 'Dataset size is not available'
            self.add_err_msg(user_msg)
            logger.error(f'ValidateReleaseUtil.run_preliminary_steps: {user_msg}')
            return False

        # Make sure the total epsilon is valid
        self.max_epsilon = self.analysis_plan.dataset.depositor_setup_info.epsilon
        self.max_delta = self.analysis_plan.dataset.depositor_setup_info.delta

        epsilon_ok, _err_msg_or_None = self.is_epsilon_valid(self.max_epsilon)
        if not epsilon_ok:
            user_msg = f'{astatic.ERR_MSG_BAD_TOTAL_EPSILON}: {self.max_epsilon}'
            self.add_err_msg(user_msg)
            logger.error(f'ValidateReleaseUtil.run_preliminary_steps: {user_msg}')
            return False

        try:
            validate_not_negative(self.max_delta)
        except ValidationError as _err_obj:
            user_msg = f'{astatic.ERR_MSG_BAD_TOTAL_DELTA}: {self.max_delta}'
            self.add_err_msg(user_msg)
            logger.error(f'ValidateReleaseUtil.run_preliminary_steps: {user_msg}')
            return False

        return True

    @staticmethod
    def is_epsilon_valid(val):
        """Validate a val as epsilon"""
        try:
            validate_epsilon_not_null(val)
        except ValidationError as err_obj:
            logger.error(f'ValidateReleaseUtil.is_epsilon_valid: {err_obj}')
            return False, str(err_obj)

        return True, None
