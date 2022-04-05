import logging

from django.conf import settings

from opendp.accuracy import laplacian_scale_to_accuracy
from opendp.trans import *
from opendp.meas import *
from opendp.mod import enable_features, binary_search_param, OpenDPException
from opendp.typing import *

from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.profiler.static_vals import VAR_TYPE_INTEGER, VAR_TYPE_CATEGORICAL

enable_features("floating-point", "contrib")


logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DPHistogramIntegerSpec(StatSpec):
    """
    Create a Histogram using integer data
    """
    STATISTIC_TYPE = astatic.DP_HISTOGRAM   #_INTEGER

    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        super().__init__(props)
        self.noise_mechanism = astatic.NOISE_GEOMETRIC_MECHANISM

    def additional_required_props(self):
        """
        Add a list of required properties
        example: ['min', 'max']
        """
        return ['min', 'max']

    def run_01_initial_handling(self):
        """
        Make sure input parameters are the correct type (fixed_value, min, max, etc.)
        Create `self.categories` based on the min/max
        """
        if not self.statistic == self.STATISTIC_TYPE:
            self.add_err_msg(f'The specified "statistic" is not "{self.STATISTIC_TYPE}".')
            return

        if not self.var_type == VAR_TYPE_INTEGER:
            user_msg = (f'The specified variable type ("var_type")'
                        f' is not "{VAR_TYPE_INTEGER}". ({self.STATISTIC_TYPE})')

            self.add_err_msg(user_msg)
            return

        # Check the fixed_value, min, max -- makes sure they're integers
        #
        if self.missing_values_handling == astatic.MISSING_VAL_INSERT_FIXED:
            # Convert the impute value to a float!
            if not self.cast_property_to_int('fixed_value'):
                return

        if not self.cast_property_to_int('min'):
            return

        if not self.cast_property_to_int('max'):
            return

        # Make sure the fixed value is between the min/max
        #
        self.check_numeric_fixed_value()

        # Create categories
        #
        self.categories = [x for x in range(self.min, self.max+1)]

    def run_03_custom_validation(self):
        """
        This is a place for initial checking/transformations
        such as making sure values are floats
        Example:
        self.check_numeric_fixed_value()
        """
        if self.has_error():
            return

    def check_scale(self, scale, preprocessor):
        """
        Return T/F
        :param scale:
        :param preprocessor:
        :return:
        """
        if self.has_error():
            return

        return preprocessor >> make_base_geometric(scale, D=VectorDomain[AllDomain[int]])

    def get_preprocessor(self):
        """
        Set up and return computation chain
        Note: Exceptions are caught via "is_chain_valid()"
        :return:
        """
        if self.has_error():
            return

        # Have we already already assembled it?
        #
        if self.preprocessor is not None:
            # Yes!
            return self.preprocessor

        preprocessor = (
            make_select_column(key=self.col_index, TOA=str) >>
            make_cast(TIA=str, TOA=int) >>
            make_impute_constant(self.fixed_value) >>
            make_count_by_categories(categories=self.categories, MO=L1Distance[int], TIA=int)
        )

        self.scale = binary_search_param(
            lambda s: self.check_scale(s, preprocessor), d_in=1, d_out=self.epsilon)
        preprocessor = preprocessor >> make_base_geometric(scale=self.scale, D=VectorDomain[AllDomain[int]])

        # keep a pointer to the preprocessor in case it's re-used
        self.preprocessor = preprocessor
        return preprocessor

    def set_accuracy(self):
        """Return the accuracy measure using Laplace and the confidence level alpha"""
        if self.has_error():
            return False

        if not self.preprocessor:
            self.preprocessor = self.get_preprocessor()

        # This is for histograms, so divide alpha by the number of counts
        cl_alpha = self.get_confidence_level_alpha() / len(self.categories)
        if cl_alpha is None:
            # Error already saved
            return False
        self.accuracy_val = laplacian_scale_to_accuracy(self.scale, cl_alpha)

        # Note `self.accuracy_val` must bet set before using `self.get_accuracy_text()
        self.accuracy_msg = self.get_accuracy_text(template_name='analysis/dp_histogram_accuracy_default.html')

        return True

    def run_chain(self, column_names, file_obj, sep_char=","):
        """
        Calculate the stats! See "dp_mean_spec.py" for an example of instantiation

        :param columns, Example: [0, 1, 2, 3] or ['a', 'b', 'c', 'd'] -- depends on your stat!
                - In general using zero-based index of columns is preferred
        :param file_obj - file like object to read data from
        :param sep_char - separator from the object, default is "," for a .csv, etc

        :return bool -  False: error messages are available through .get_err_msgs()
                                or .get_error_msg_dict()
                        True: results available through .value -- others params through
                                .get_success_msg_dict()

        Example:
        # Note "\t" is for a tabular file
        `dp_mean_spec.run_chain([0, 1, 2, 3], file_obj, sep_char="\t")`
        """
        if not self.preprocessor:
            assert False, 'Please call is_chain_valid() before using "run_chain()!'

        self.value = None

        if self.has_error():
            return False

        if not isinstance(column_names, list):
            self.add_err_msg('DPHistogramSpec.run_chain(..): column_names must be a list. Found: (type({column_names}))')
            return

        try:
            parse_dataframe = make_split_dataframe(separator=sep_char,
                                                   col_names=column_names)

            computation_chain = parse_dataframe >> self.preprocessor

            self.value = computation_chain(file_obj.read())

        except OpenDPException as ex_obj:
            logger.exception(ex_obj)
            self.add_err_msg(f'{ex_obj.message} (OpenDPException)')
            return False
        except Exception as ex_obj:
            if hasattr(ex_obj, 'message'):
                self.add_err_msg(f'{ex_obj.message} (Exception)')
            else:
                self.add_err_msg(f'{ex_obj} (Exception)')
            return False

        fmt_categories = self.categories + ['uncategorized']

        # Show warning if category count doesn't match values count
        if len(fmt_categories) > len(self.value):

            user_msg = (f'Warning. There are more categories (n={len(self.fmt_categories)})'
                        f' than values (n={len(self.value)})')
            self.add_err_msg(user_msg)

            logger.warning(user_msg)
            logger.warning(f'Categories (n={len(self.categories)}): {self.categories}')
            logger.warning(f'Values (n={len(self.value)}): {self.value}')
            return


        self.value = dict(categories=fmt_categories,
                          values=self.value,
                          category_value_pairs=list(zip(fmt_categories, self.value)))


        logger.info((f"Epsilon: {self.epsilon}"
                     f"\nColumn name: {self.variable}"
                     f"\nColumn index: {self.col_index}"
                     f"\nAccuracy value: {self.accuracy_val}"
                     f"\nAccuracy message: {self.accuracy_msg}"
                     f"\n\nDP Histogram: {self.value}" ))

        return True