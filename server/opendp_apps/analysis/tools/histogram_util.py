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
    Boolean            X (c)            na             na

    @param props:
    @return: StatSpec of the correct Histogram type
    """
    # print('>> (30) get_histogram_stat_spec / props: ', dict(props))
    var_type = props.get('var_type')
    histogram_bin_type = props.get(astatic.KEY_HIST_BIN_TYPE, astatic.HIST_BIN_TYPE_ONE_PER_VALUE)

    # Boolean
    if var_type == pstatic.VAR_TYPE_BOOLEAN and histogram_bin_type == astatic.HIST_BIN_TYPE_ONE_PER_VALUE:
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
