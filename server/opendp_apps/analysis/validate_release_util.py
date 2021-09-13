"""Utility class utilized by DRF API endpoints"""

from django.contrib.auth import get_user_model

from opendp_apps.analysis.analysis_plan_util import AnalysisPlanUtil
from opendp_apps.analysis.stat_valid_info import StatValidInfo
from opendp_apps.analysis.tools.dp_mean import dp_mean

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.utils.camel_to_snake import camel_to_snake



class ValidateReleaseUtil(BasicErrCheck):

    def __init__(self, opendp_user: get_user_model(), analysis_plan_id: int, dp_statistics: list, release_run=False, **kwargs):
        """Passing IDs instead of objects here makes it easier to run async via celery, etc."""
        self.opendp_user = opendp_user     # to be retrieved

        self.analysis_plan_id = analysis_plan_id
        self.analysis_plan = None       # to be retrieved

        self.dp_statistics = dp_statistics

        self.validation_info = []      # list of StatValidInfo objects as dicts to return to UI

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
        for dp_stat in self.dp_statistics:
            stat_num += 1       # not used yet...
            statistic = dp_stat['statistic']
            var_name = camel_to_snake(dp_stat['variable'])  # User "variable", NOT "label"

            # Get the variable info
            variable_info = self.analysis_plan.variable_info.get(var_name)
            if not variable_info:
                info = StatValidInfo.get_error_msg_dict(var_name, statistic, 'Variable info not found.')
                self.validation_info.append(info)
                continue # to the next dp_stat specification

            # Fine the min/max in the variable info
            lower = variable_info.get('min')
            if lower is None:
                info = StatValidInfo.get_error_msg_dict(var_name, statistic, '"min" must be defined.')
                self.validation_info.append(info)
                continue # to the next dp_stat specification

            upper = variable_info.get('max')
            if upper is None:
                info = StatValidInfo.get_error_msg_dict(var_name, statistic, '"max" must be defined.')
                self.validation_info.append(info)
                continue # to the next dp_stat specification

            # Retrieve the column index
            #
            col_idx_info = self.analysis_plan.dataset.get_variable_index(var_name)
            if not col_idx_info.success:
                info = StatValidInfo.get_error_msg_dict(var_name, statistic, col_idx_info.message)
                self.validation_info.append(info)
                continue  # to the next dp_stat specification
            col_idx = col_idx_info.data

            # Retrieve the dataset size
            #   -> Needs updating to related to DP questions!
            #
            dataset_size_info = self.analysis_plan.dataset.get_dataset_size()
            if not dataset_size_info.success:
                info = StatValidInfo.get_error_msg_dict(var_name, statistic, dataset_size_info.message)
                self.validation_info.append(info)
                continue  # to the next dp_stat specification
            dataset_size = dataset_size_info.data

            # Find the column index
            index = 0  # TODO: column headers.... (variable_info['index'])

            impute = dp_stat['missing_values_handling'] != astatic.MISSING_VAL_DROP
            impute_value = float(dp_stat['fixed_value'])
            epsilon = float(dp_stat['epsilon'])

            # Do some validation and append to stats_valid
            if statistic == astatic.DP_MEAN:
                try:
                    # print(index, lower, upper, n, impute_value, dp_stat['epsilon'])
                    # print(list(map(type, (index, lower, upper, n, impute_value, dp_stat['epsilon']))))
                    preprocessor = dp_mean(col_idx, lower, upper, dataset_size, impute_value, epsilon)
                    # TODO: add column index and statistic to result
                    self.validation_info.append(StatValidInfo.get_success_msg_dict(var_name, statistic))
                    continue  # to the next dp_stat specification
                except Exception as ex:
                    info = StatValidInfo.get_error_msg_dict(var_name, statistic, str(ex))
                    continue  # to the next dp_stat specification
            else:
                user_msg = f'Statistic \'{statistic}\' is not supported'
                info = StatValidInfo.get_error_msg_dict(var_name, statistic, user_msg)
                continue  # to the next dp_stat specification



    def run_preliminary_steps(self):
        """Run preliminary steps before validation"""

        # Retrieve the Analysis Plan
        #
        ap_info = AnalysisPlanUtil.retrieve_analysis(self.opendp_user.object_id, self.opendp_user)
        if not ap_info.succsss:
            self.add_err_msg(ap_info.message)
            return False

        self.analysis_plan = ap_info.data

        # Check the dp_statistics spec
        #
        if not self.dp_statistics:
            user_msg = 'There are no statistics to validate'
            self.add_err_msg(ap_info.message)
            return False

        return True

