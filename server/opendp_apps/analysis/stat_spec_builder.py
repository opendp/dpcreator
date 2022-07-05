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

    def __init__(self, analysis_plan: AnalysisPlan,
                 dp_statistics: list = None, is_private_count: bool = False, **kwargs):
        """
        Note: Do not use the __init__ directly, use one of these static methods:
            - build_with_public_count(...)
            - build_with_private_count(...)
        """
        self.analysis_plan = analysis_plan
        self.dp_statistics = dp_statistics
        self.is_private_count = is_private_count

        self.stat_spec_list = []
        self.dataset_size = None

        self.build_stat_specs()


    @staticmethod
    def build_with_public_count(analysis_plan: AnalysisPlan, dp_statistics: list = None, **kwargs):
        """Create a StatSpecBuilder where there the dataset size is public"""
        return StatSpecBuilder(analysis_plan, dp_statistics, False, **kwargs)

    @staticmethod
    def build_with_private_count(analysis_plan: AnalysisPlan, dp_statistics: list = None, **kwargs):
        """Create a StatSpecBuilder where there the dataset size remains private"""
        return StatSpecBuilder(analysis_plan, dp_statistics, True, **kwargs)

    def determine_dataset_size(self):
        """Depending on 'is_private_count" and the contents of `dp_statistics`, determine the dataset size"""

        # May the dataset size be made public?


    def build_stat_specs(self):
        """
        Build a list of StatSpec subclasses that can be used for
        chain validation or running computations
        """
        if self.has_error():
            return

        self.determine_dataset_size()

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
