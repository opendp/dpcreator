"""
Return the correct Histogram StatSpec depending on the input properties
"""
import copy

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.dp_histogram_boolean_spec import DPHistogramBooleanSpec
from opendp_apps.analysis.tools.dp_histogram_categorical_spec import DPHistogramCategoricalSpec
from opendp_apps.analysis.tools.dp_histogram_int_bin_edges_spec import DPHistogramIntBinEdgesSpec
from opendp_apps.analysis.tools.dp_histogram_int_equal_ranges_spec import DPHistogramIntEqualRangesSpec
from opendp_apps.analysis.tools.dp_histogram_int_one_per_value_spec import DPHistogramIntOnePerValueSpec
from opendp_apps.analysis.tools.dp_spec_error import DPSpecError
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.profiler import static_vals as pstatic


def get_histogram_stat_spec(props: dict) -> StatSpec:
    """
    Make sure that the variable type is appropriate for the histogram settings.
        (e) = edges
        (c) = categories
        na = not applicable

    Data Type	    onePerValue	    equalRanges	    binEdges
    Categorical        X (c)            na             na
    Integer	           X (c)            X (e)          X (e)
    Float		       na               X (e)          X (e)*
    Boolean            na               na             na

    @param props:
    @return: StatSpec of the correct Histogram type
    """
    var_type = props.get('var_type')

    # Boolean
    if var_type == pstatic.VAR_TYPE_BOOLEAN:
        return DPHistogramBooleanSpec(props)

    elif var_type == pstatic.VAR_TYPE_CATEGORICAL:
        # Categorical
        # Technically, can only have bin type OnePerValue
        # 4/12/2022 - temp hack to distinguish numeric categories
        #   - need updated UI, etc.
        #
        has_int_cats, _min_max = has_integer_categories(props)
        if has_int_cats:
            # Artificially set the min/max
            #
            props['variable_info']['type'] = pstatic.VAR_TYPE_INTEGER
            props['variable_info']['min'] = _min_max[0]
            props['variable_info']['max'] = _min_max[1]
            return DPHistogramIntOnePerValueSpec(props)
        else:
            # Can only have bin type OnePerValue
            return DPHistogramCategoricalSpec(props)

    elif var_type == pstatic.VAR_TYPE_INTEGER:
        # OnePerValue
        if histogram_bin_type == astatic.HIST_BIN_TYPE_ONE_PER_VALUE:
            return DPHistogramIntOnePerValueSpec(props)

        elif histogram_bin_type == astatic.HIST_BIN_TYPE_EQUAL_RANGES:
            # EqualRanges
            return DPHistogramIntEqualRangesSpec(props)

        elif histogram_bin_type == astatic.HIST_BIN_TYPE_BIN_EDGES:
            # BinEdges
            return DPHistogramIntBinEdgesSpec(props)

        else:
            # Unknown bin type
            props['error_message'] = f'Unknown histogram_bin_type: "{histogram_bin_type}"'
            return DPSpecError(props)

    elif var_type == pstatic.VAR_TYPE_FLOAT:
        # Float
        assert False, 'Histograms are not available for Floats.'

    else:
        # Unknown bin type
        props['error_message'] = f'Unknown variable type: "{var_type}"'
        return DPSpecError(props)


def has_integer_categories(props: dict):
    """
    4/12/2022 - temporary hack for histograms
    Check if the props['variable_info']['categories'] list consists of continuous integers

    @param props: dict
    @return: tuple
        if False: (False, None)
        if True: (True, (min, max))
    """
    if not props:
        return False, None

    # Are there categories?
    if ('variable_info' in props) and ('categories' in props['variable_info']):

        # Get the categories
        cats = copy.deepcopy(props['variable_info']['categories'])

        # Are all the values integers?
        all_int_check = [isinstance(x, int) for x in cats]

        # Nope, return
        if False in all_int_check:
            return False, None

        # They're all integers, but are they continuous?
        if sorted(cats) == list(range(min(cats), max(cats) + 1)):
            return True, (min(cats), max(cats))

    return False, None


'''
class HistogramUtil(BasicErrCheck):


    def __init__(self, stat_spec: StatSpec):
        """

        @param stat_spec: Should be for a histogram, e.g. DPHistogramIntOnePerValueSpec, etc
        """
        self.stat_spec = stat_spec


        self.run_process()

    def use_bin_edges(self):
        """Check if edges should be retrieved--if not use categories"""
        assert self.has_error() is False, \
            "Check that .has_error() is False before calling this method"

        return self.expect_edges

    def get_bin_edges(self) -> list:
        """
        Return calculated edges.
        Check that .has_error() is True before calling this method
        @return:
        """
        assert self.has_error() is False, \
            "Check that .has_error() is False before calling this method"

        return self.bin_edges

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

        # self.create_categories()

    def xcreate_categories(self) -> bool:
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
            self.categories = self.stat_spec.categories
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
        if not self.validate_property(self.stat_spec.histogram_number_of_bins,
                                      validate_int_greater_than_zero,
                                      'hist_number_of_bins'):
            return False

        # Make sure there aren't more bins than values
        #
        num_items = self.stat_spec.max - self.stat_spec.min
        if self.stat_spec.histogram_number_of_bins > num_items:
            user_msg = ('There are more bins than values.'
                        ' (hist_number_of_bins)')
            self.add_err_msg(user_msg)
            return False

        # set bin_edges
        min_max = (self.stat_spec.min, self.stat_spec.max)
        bin_edges = np.histogram_bin_edges(
            [],
            bins=self.stat_spec.histogram_number_of_bins,
            range=min_max)

        # Note: adding 1 to the max, which includes the max in the last bin
        self.bin_edges = [int(x) for x in bin_edges[:-1]] + [self.stat_spec.max + 1]
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
'''
