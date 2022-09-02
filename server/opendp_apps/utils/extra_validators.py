from typing import Any, Union

from django.conf import settings
from django.core.exceptions import ValidationError

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.profiler import static_vals as pstatic

VALIDATE_MSG_ZERO_OR_GREATER = 'The value must be a number, zero or greater.'
VALIDATE_MSG_ONE_OR_GREATER = 'The value must be a number, 1 or greater.'
VALIDATE_MSG_TWO_OR_GREATER = 'The value must be an integer, 2 or greater.'
VALIDATE_MSG_EPSILON = (f'As a rule of thumb, epsilon should not be less than'
                        f' {settings.TOTAL_EPSILON_MIN} nor greater than {settings.TOTAL_EPSILON_MAX}.')
VALIDATE_MSG_NOT_FLOAT = 'The value must be a float.'
VALIDATE_MSG_NOT_INT = 'The value must be an integer.'
VALIDATE_MSG_NOT_VALID_CL_VALUE = 'Valid confidence level values:'
VALIDATE_MSG_MISSING_VAL_HANDLER = 'Valid missing value handlers:'
VALIDATE_MSG_UNSUPPORTED_STATISTIC = 'Valid statistics:'

VALIDATE_MSG_CATEGORIES_NOT_A_LIST = 'The "categories" variable is not a list'
VALIDATE_MSG_CATEGORIES_LIST_EMPTY = 'The list of categories is empty'
VALIDATE_MSG_CATEGORY_NOT_STRING = 'The list of categories contains a non-string'  # Only used for categorical variables
VALIDATE_MSG_FIXED_VAL_NOT_IN_CATEGORIES = 'The fixed value is not one of the specified categories.'

VALIDATE_MSG_TWO_EDGES_MINIMUM = 'At least two edges are needed to create the histogram.'
VALIDATE_MSG_EDGES_NOT_A_LIST = 'The "edges" are not a list'


def validate_statistic(value):
    """Statistic currently supported"""
    if value not in astatic.DP_STATS_CHOICES:
        ch_choices_str = ', '.join(astatic.DP_STATS_CHOICES)
        user_msg = f'{VALIDATE_MSG_UNSUPPORTED_STATISTIC} {ch_choices_str}'
        raise ValidationError(user_msg)


def validate_confidence_level(value):
    """Validate a valid confidence level value"""
    validate_float(value)
    #
    valid_cl_choices = [x[0] for x in astatic.CL_CHOICES]

    if value not in valid_cl_choices:
        # CL_CHOICES = [x[0] for x in astatic.CL_CHOICES]
        ch_choices_str = ', '.join([str(x) for x in valid_cl_choices])
        user_msg = f'{VALIDATE_MSG_NOT_VALID_CL_VALUE} {ch_choices_str}'
        raise ValidationError(user_msg)


def validate_missing_val_handlers(value):
    """Check that the missing val handler is correct"""
    if value not in astatic.MISSING_VAL_HANDLING_TYPES:
        choices_str = ', '.join(astatic.MISSING_VAL_HANDLING_TYPES)
        user_msg = f'{VALIDATE_MSG_MISSING_VAL_HANDLER} {choices_str}'
        raise ValidationError(user_msg)


def validate_not_negative(value):
    """Valid values are non-negative numbers"""
    validate_float(value)

    if value < 0.0:
        raise ValidationError(VALIDATE_MSG_ZERO_OR_GREATER)


def validate_edge_count_two_or_greater(value: list):
    """Validate that the length of the list of edges is at least 2"""
    if not isinstance(value, list):
        raise ValidationError(VALIDATE_MSG_EDGES_NOT_A_LIST)

    if len(value) >= 2:
        pass
    else:
        raise ValidationError(VALIDATE_MSG_TWO_EDGES_MINIMUM)


def validate_int_two_or_greater(value):
    """Validate int greater >= 2"""
    if not isinstance(value, int):
        raise ValidationError(VALIDATE_MSG_NOT_INT)

    if value >= 2:
        pass
    else:
        raise ValidationError(VALIDATE_MSG_TWO_OR_GREATER)


def validate_int_greater_than_zero(value):
    """Validate int greater >= 1"""
    if not isinstance(value, int):
        raise ValidationError(VALIDATE_MSG_NOT_INT)

    if value < 1:
        raise ValidationError(VALIDATE_MSG_ONE_OR_GREATER)


def validate_int_not_negative(value):
    """Validate int greater >= 0"""
    if not isinstance(value, int):
        raise ValidationError(VALIDATE_MSG_NOT_INT)

    if value < 0:
        raise ValidationError(VALIDATE_MSG_ZERO_OR_GREATER)


def validate_not_negative_or_none(value):
    """Valid values are None or non-negative numbers"""
    if value is None:
        # okay value!
        return

    validate_float(value)
    validate_not_negative(value)


def validate_epsilon_or_none(value):
    """
    May be None or a valid epsilon value
    """
    if value is None:
        # okay value!
        return

    validate_epsilon_not_null(value)


def validate_not_empty_or_none(value):
    if value == 0:
        pass
    elif not value:
        raise ValidationError('The value cannot be empty.')


def validate_not_none(value):
    if value is None:
        raise ValidationError('The value cannot be None.')


def validate_epsilon_not_null(value):
    """
    As a rule of thumb, however, epsilon should be thought of as a small number,
    between approximately  1/100 and 1
    source: https://admindatahandbook.mit.edu/book/v1.0/diffpriv.html
    """
    validate_float(value)

    if value > settings.TOTAL_EPSILON_MAX or value < settings.TOTAL_EPSILON_MIN:
        raise ValidationError(VALIDATE_MSG_EPSILON)


def validate_float(value):
    """Make sure the value is a float"""
    try:
        float(value)
    except ValueError:
        raise ValidationError(VALIDATE_MSG_NOT_FLOAT)
    except TypeError:
        raise ValidationError(VALIDATE_MSG_NOT_FLOAT)


def validate_int(value):
    """Make sure the value is a float"""
    try:
        int(value)
    except ValueError:
        raise ValidationError(VALIDATE_MSG_NOT_INT)
    except TypeError:
        raise ValidationError(VALIDATE_MSG_NOT_INT)


def validate_is_numeric(value: Union[int, float]):
    """Check that the value is an integer or float"""
    validate_float(value)
    validate_int(value)


def validate_type_numeric(value: str):
    """Make sure the variable type is integer or float"""
    if value not in pstatic.NUMERIC_VAR_TYPES:
        raise ValidationError(pstatic.ERR_MSG_VAR_TYPE_NOT_NUMERIC)


def validate_type_categorical(value: str):
    """Make sure the variable type is integer or float"""
    if not value == pstatic.VAR_TYPE_CATEGORICAL:
        raise ValidationError(pstatic.ERR_MSG_VAR_TYPE_NOT_CATEGORICAL)


def validate_type_integer(value: str):
    """Make sure the variable type is integer or float"""
    if not value == pstatic.VAR_TYPE_INTEGER:
        raise ValidationError(pstatic.ERR_MSG_VAR_TYPE_NOT_INTEGER)


def validate_categories_as_list(categories: list):
    if not isinstance(categories, list):
        raise ValidationError(VALIDATE_MSG_CATEGORIES_NOT_A_LIST)


def validate_categories_list_not_empty(categories: list):
    """Make sure the categories are a non-empty list"""
    validate_categories_as_list(categories)

    if len(categories) == 0:
        raise ValidationError(VALIDATE_MSG_CATEGORIES_LIST_EMPTY)


def validate_categories_as_string(categories: list):
    """Check that there are items in the list and each one is a string"""
    validate_categories_list_not_empty(categories)

    for x in categories:
        if not isinstance(x, str):
            raise ValidationError(VALIDATE_MSG_CATEGORY_NOT_STRING + ': ' + type(x))

    # cat_as_strings = [isinstance(x, str) for x in categories]
    # if False in cat_as_strings


def validate_fixed_value_in_categories(fixed_value: Any, categories: list):
    """

    @param fixed_value: any type of value
    @param categories: list of values
    @return:
    """
    validate_categories_list_not_empty(categories)

    if fixed_value not in categories:
        raise ValidationError(VALIDATE_MSG_FIXED_VAL_NOT_IN_CATEGORIES)


def validate_histogram_bin_type(bin_type: str):
    """
    @param bin_type: expecting one of astatic.HIST_VALID_BIN_TYPES
    @return:
    """
    if bin_type not in astatic.HIST_VALID_BIN_TYPES:
        raise ValidationError(astatic.ERR_MSG_HIST_BIN_TYPE_UKNOWN)


def validate_histogram_bin_type_one_per_value(bin_type: str):
    """
    @param bin_type: expecting astatic.HIST_BIN_TYPE_ONE_PER_VALUE
    @return:
    """
    if not bin_type == astatic.HIST_BIN_TYPE_ONE_PER_VALUE:
        raise ValidationError(f'Expected histogram bin type to be "{astatic.HIST_BIN_TYPE_ONE_PER_VALUE}"')


def validate_histogram_bin_type_equal_ranges(bin_type: str):
    """
    @param bin_type: expecting astatic.HIST_BIN_TYPE_EQUAL_RANGES
    @return:
    """
    if not bin_type == astatic.HIST_BIN_TYPE_EQUAL_RANGES:
        raise ValidationError(f'Expected histogram bin type to be "{astatic.HIST_BIN_TYPE_EQUAL_RANGES}"')


def validate_histogram_bin_type_edges(bin_type: str):
    """
    @param bin_type: expecting astatic.HIST_BIN_TYPE_EQUAL_RANGES
    @return:
    """
    if not bin_type == astatic.HIST_BIN_TYPE_BIN_EDGES:
        raise ValidationError(f'Expected histogram bin type to be "{astatic.HIST_BIN_TYPE_BIN_EDGES}"')


def validate_min_max(min_int: Union[int, float], max_int: Union[int, float]):
    """
    If it applies, validate the min/max relationship
    """
    validate_is_numeric(min_int)
    validate_is_numeric(max_int)

    if not max_int > min_int:
        user_msg = f'{astatic.ERR_MAX_NOT_GREATER_THAN_MIN} (max: {max_int}, min: {min_int})'
        raise ValidationError(user_msg)


def validate_fixed_value_against_min_max(fixed_value: Union[int, float],
                                         min_int: Union[int, float],
                                         max_int: Union[int, float]):
    validate_is_numeric(fixed_value)
    validate_is_numeric(min_int)
    validate_is_numeric(max_int)

    if fixed_value < min_int:
        user_msg = (f'The "fixed value" ({fixed_value})'
                    f' {astatic.ERR_IMPUTE_PHRASE_MIN} ({min_int})')
        raise ValidationError(user_msg)
    elif fixed_value > max_int:
        user_msg = (f'The "fixed value" ({fixed_value})'
                    f' {astatic.ERR_IMPUTE_PHRASE_MAX} ({max_int})')
        raise ValidationError(user_msg)


def validate_num_bins_against_min_max(histogram_number_of_bins: int, min_int: int, max_int: int):
    """
    Check that the number of bins isn't more than the number of values

    @param histogram_number_of_bins:
    @param min_int:
    @param max_int:
    @return:
    """
    validate_int_greater_than_zero(histogram_number_of_bins)  # may be redundant
    validate_min_max(min_int, max_int)

    potential_num_values = max_int - min_int

    if histogram_number_of_bins > potential_num_values:
        user_msg = (f'There are more bins than values.'
                    f' (hist_number_of_bins: {histogram_number_of_bins}) (# values: {potential_num_values})')
        raise ValidationError(user_msg)
