"""
Validate histogram specs and, if needed, generate categories.

Within a StatSpec, this class should be used in the function "run_03_custom_validation()", e.g.

    histogram_util = histogram_util(self)
    if histogram_util.has_error():
        self.add_error_msg(histogram_util.get_error_message())
        return
    else:
        if histogram_util.has_categories():
            self.categories = histogram_util.get_categories()
"""
import numpy as np
from django.core.exceptions import ValidationError

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.utils.extra_validators import \
    (validate_histogram_bin_type,
     validate_histogram_bin_type_one_per_value,
     validate_histogram_bin_type_equal_ranges_or_edges,
     validate_int_greater_than_zero)


class HistogramUtil(BasicErrCheck):

    def __init__(self, stat_spec: StatSpec):
        """

        @param stat_spec: Should be for a histogram, e.g. DPHistogramIntegerSpec, etc
        """
        self.stat_spec = stat_spec

        self.expect_edges = True
        self.categories = None  # Generate categories if needed
        self.bin_edges = None

        self.run_process()

    def use_edges(self):
        """Check if edges should be retrieved--if not use categories"""
        assert self.has_error() is False, \
            "Check that .has_error() is False before calling this method"

        return self.expect_edges

    def get_edges(self) -> list:
        """
        Return calculated edges.
        Check that .has_error() is True before calling this method
        @return:
        """
        assert self.has_error() is False, \
            "Check that .has_error() is False before calling this method"

        return self.edges

    def get_categories(self) -> list:
        """
        Return calculated categories.
        Check that .has_categories() is True before calling this method
        @return:
        """
        assert self.has_error() is False, \
            "Check that .has_error() is False before calling this method"

        return self.categories

    def run_process(self):
        """
        @return:
        """
        if self.has_error():
            return

        if not self.validate_histogram_props():
            return

        self.create_categories()

    def create_categories(self) -> bool:
        """
        If applicable, create categories
        @return:
        """
        if self.has_error():
            return False

        if self.stat_spec.histogram_bin_type == astatic.HIST_BIN_TYPE_ONE_PER_VALUE:
            return True

        if self.stat_spec.histogram_bin_type == astatic.HIST_BIN_TYPE_EQUAL_RANGES:
            pass

    def validate_histogram_props(self) -> bool:
        """
        Make sure that the variable type is appropriate for the histogram settings.
            (e) = edges
            (c) = categories

        Data Type	    onePerValue	    equalRanges	    binEdges
        Categorical        X (c)
        Integer	           X (c)            X (e)          X (e)
        Float		                        X (e)          X (e)*

        @return:
        """
        if self.has_error():
            return False

        # Categorical
        if self.stat_spec.var_type == pstatic.VAR_TYPE_CATEGORICAL:
            # Can only have bin type OnePerValue
            self.expect_edges = False
            if not self.validate_property(self.stat_spec.histogram_bin_type,
                                          validate_histogram_bin_type_one_per_value,
                                          'histogram_bin_type'):
                return False
            return True

        # Integer
        if self.stat_spec.var_type == pstatic.VAR_TYPE_INTEGER:
            # Any bin type is okay
            if not self.validate_property(self.stat_spec.histogram_bin_type,
                                          validate_histogram_bin_type,
                                          'histogram_bin_type'):
                return False

            return self.construct_integer_categories()

        # Float
        if self.stat_spec.var_type == pstatic.VAR_TYPE_FLOAT:
            if not self.validate_property(self.stat_spec.histogram_bin_type,
                                          validate_histogram_bin_type_equal_ranges_or_edges,
                                          'histogram_bin_type'):
                return False
            return True

        self.stat_spec.add_err_msg('Unknown variable type: "{self.stat_spec.var_type"}')
        return False

    def validate_property(self, value, validator, prop_name: str = None) -> bool:
        """Validate a property name using a validator"""
        if self.has_error():
            return False

        try:
            validator(value)
        except ValidationError as err_obj:
            user_msg = f'{err_obj.message}'
            if prop_name:
                user_msg = f'{user_msg} ({prop_name})'
            self.add_err_msg(user_msg)
            return False

        return True

    def construct_integer_categories(self) -> bool:
        """Construct categories if the values are integers"""
        assert self.stat_spec.var_type == pstatic.VAR_TYPE_INTEGER, \
            (f'This function should only be called if the "var_type" is '
             f' "{pstatic.VAR_TYPE_INTEGER}"')

        # OnePerValue
        if self.stat_spec.histogram_bin_type == astatic.HIST_BIN_TYPE_ONE_PER_VALUE:
            # Create categories
            #
            self.expect_edges = False
            self.categories = [x for x in range(self.stat_spec.min, self.stat_spec.max + 1)]
            return True

        elif self.stat_spec.histogram_bin_type == astatic.HIST_BIN_TYPE_EQUAL_RANGES:
            # EqualRanges
            return self.set_integer_edges_from_number_of_bins()

        elif self.stat_spec.histogram_bin_type == astatic.HIST_BIN_TYPE_BIN_EDGES:
            # BinEdges
            return self.set_integer_edges_from_number_of_bins()

        self.add_err_msg(astatic.ERR_MSG_HIST_BIN_TYPE_UKNOWN)
        return False


    def set_integer_edges_from_number_of_bins(self) -> bool:
        """
        For var type, integer, set the edges based on the hist_number_of_bins
        @return: bool
        """
        if not self.validate_property(self.stat_spec.hist_number_of_bins,
                                      validate_int_greater_than_zero,
                                      'hist_number_of_bins'):
            return False

        # Make sure there aren't more bins than values
        #
        num_items = self.stat_spec.max - self.stat_spec.min
        if self.stat_spec.hist_number_of_bins > num_items:
            user_msg = ('There are more bins than values.'
                        ' (hist_number_of_bins)')
            self.add_err_msg(user_msg)
            return False

        # set bin_edges
        min_max = (self.stat_spec.min, self.stat_spec.max)
        bin_edges = np.histogram_bin_edges(
                            [],
                            bins=self.stat_spec.hist_number_of_bins,
                            range=min_max)

        # Note: adding 1 to the max, which includes the max in the last bin
        self.bin_edges = [int(x) for x in bin_edges[:-1]] + int(self.max+1)
        if len(self.bin_edges) != len(list(set(self.bin_edges))):
            self.bin_edges = None
            self.add_err_msg(astatic.ERR_MSG_TOO_MANY_BINS)
            return False

        return True


"""
min = 1
max = 101
num_bins = 5
values = range(1, 101)
bin_size = len(values/num_bins)


# edges = 
"""
