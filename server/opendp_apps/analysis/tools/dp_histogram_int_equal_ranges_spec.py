import logging
from typing import Union

from django.conf import settings
from opendp.accuracy import laplacian_scale_to_accuracy
from opendp.meas import make_base_discrete_laplace
from opendp.mod import enable_features, binary_search_param, OpenDPException
from opendp.trans import \
    (make_cast,
     make_count_by_categories,
     make_find_bin,
     make_impute_constant,
     make_index,
     make_select_column,
     make_split_dataframe)
from opendp.typing import VectorDomain, AllDomain, usize

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.bin_edge_helper import BinEdgeHelper
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.utils.extra_validators import \
    (validate_fixed_value_against_min_max,
     validate_histogram_bin_type_equal_ranges,
     validate_int,
     validate_int_two_or_greater,
     validate_min_max,
     validate_missing_val_handlers,
     validate_num_bins_against_min_max,
     validate_type_integer)

enable_features("floating-point", "contrib")

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DPHistogramIntEqualRangesSpec(StatSpec):
    """
    Create a Histogram using integer data
    """
    STATISTIC_TYPE = astatic.DP_HISTOGRAM  # _INTEGER

    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        super().__init__(props)
        self.noise_mechanism = astatic.NOISE_GEOMETRIC_MECHANISM

    def get_stat_specific_validators(self):
        """Set validators used for the DP Mean"""
        return dict(histogram_bin_type=validate_histogram_bin_type_equal_ranges,
                    histogram_number_of_bins=validate_int_two_or_greater,
                    var_type=validate_type_integer,
                    #
                    min=validate_int,
                    max=validate_int,
                    #
                    missing_values_handling=validate_missing_val_handlers)

    def run_01_initial_transforms(self):
        """
        Make sure input parameters are the correct type (fixed_value, min, max, etc.)
        Create `self.categories` based on the min/max
        """
        # Cast min/max to integers
        #
        if not self.cast_property_to_int('min'):
            return

        if not self.cast_property_to_int('max'):
            return

        # validate min/max
        if not self.validate_multi_values([self.min, self.max],
                                          validate_min_max,
                                          'min/max'):
            return

        if not self.cast_property_to_int('histogram_number_of_bins'):
            return

        if not self.validate_multi_values([self.histogram_number_of_bins,
                                           self.min,
                                           self.max],
                                          validate_num_bins_against_min_max,
                                          'histogram_number_of_bins/max'):
            return

        # Check the fixed_value, min, max -- makes sure they're integers
        #
        if self.missing_values_handling == astatic.MISSING_VAL_INSERT_FIXED:
            # Convert the impute value to an int
            if not self.cast_property_to_int('fixed_value'):
                return

            if not self.validate_multi_values(
                    [self.fixed_value, self.min, self.max],
                    validate_fixed_value_against_min_max,
                    'fixed value within min/max bounds'):
                return

        beh = BinEdgeHelper(self.min, self.max, self.histogram_number_of_bins)
        if beh.has_error():
            self.add_err_msg(beh.get_err_msg())
            return

        self.histogram_bin_edges = beh.bin_edges
        self.categories = beh.buckets

    def run_03_custom_validation(self):
        """
        No further checking needed
        """
        pass

    def check_scale(self, scale, preprocessor):
        """
        Return T/F
        :param scale:
        :param preprocessor:
        :return:
        """
        if self.has_error():
            return

        return preprocessor >> make_base_discrete_laplace(scale, D=VectorDomain[AllDomain[int]])

        # return preprocessor >> make_base_geometric(scale, D=VectorDomain[AllDomain[int]])

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

        categories_list = self.get_pseudo_categories_list()

        # Note: earlier validation checks that "self.histogram_number_of_bins" is > 2
        num_bin_edges = len(self.histogram_bin_edges)
        null_bin = num_bin_edges - 1

        preprocessor = (
                make_select_column(key=self.col_index, TOA=str) >>
                make_cast(TIA=str, TOA=int) >>
                make_impute_constant(self.fixed_value) >>
                make_find_bin(edges=self.histogram_bin_edges) >>
                make_index([null_bin, *range(null_bin), null_bin],
                           null_bin,
                           TOA=usize) >>
                make_count_by_categories(categories=categories_list,
                                         TIA=usize)
        )

        def make_histogram(scale):
            return preprocessor >> \
                   make_base_discrete_laplace(
                       scale, D=VectorDomain[AllDomain[int]])

        self.scale = binary_search_param(
            make_histogram,
            d_in=1,
            d_out=self.epsilon)

        preprocessor = make_histogram(self.scale)

        # keep a pointer to the preprocessor in case it's re-used
        self.preprocessor = preprocessor
        return preprocessor

    def get_pseudo_categories_list(self) -> Union[list, None]:
        """
        Not the actual categories, used for setting accuracy, etc

        @return: Union[list, None]
        """
        if self.has_error():
            return None

        return list(range(len(self.histogram_bin_edges)))

    def set_accuracy(self):
        """Return the accuracy measure using Laplace and the confidence level alpha"""
        if self.has_error():
            return False

        self.accuracy_val = 'Made up val'
        self.accuracy_msg = self.get_accuracy_text(template_name='analysis/dp_histogram_accuracy_default.txt')
        return True

        if not self.preprocessor:
            self.preprocessor = self.get_preprocessor()

        # This is for histograms, so divide alpha by the number of counts
        # we just need the length, using the number of bin edges
        categories_list = self.get_pseudo_categories_list()

        cl_alpha = self.get_confidence_level_alpha() / len(categories_list)
        if cl_alpha is None:
            # Error already saved
            return False

        self.accuracy_val = laplacian_scale_to_accuracy(self.scale, cl_alpha)

        # Note `self.accuracy_val` must bet set before using `self.get_accuracy_text()
        self.accuracy_msg = self.get_accuracy_text(template_name='analysis/dp_histogram_accuracy_default.txt')

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
            self.add_err_msg(
                'DPHistogramSpec.run_chain(..): column_names must be a list. Found: (type({column_names}))')
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

        print('self.histogram_bin_edges', self.histogram_bin_edges)
        print('self.value', self.value)

        # Show warning if category count doesn't match values count
        if len(self.categories) > len(self.value):
            user_msg = (f'Warning. There are more categories (n={len(self.categories)})'
                        f' than values (n={len(self.value)})')
            self.add_err_msg(user_msg)

            logger.warning(user_msg)
            logger.warning(f'Categories (n={len(self.categories)}): {self.categories}')
            logger.warning(f'Values (n={len(self.value)}): {self.value}')
            return

        self.value = dict(categories=self.categories,
                          values=self.value,
                          category_value_pairs=list(zip(self.categories, self.value)))

        logger.info((f"Epsilon: {self.epsilon}"
                     f"\nColumn name: {self.variable}"
                     f"\nColumn index: {self.col_index}"
                     f"\nAccuracy value: {self.accuracy_val}"
                     f"\nAccuracy message: {self.accuracy_msg}"
                     f"\n\nDP Histogram: {self.value}"))

        return True
