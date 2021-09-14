from django.core.exceptions import ValidationError

from opendp_apps.analysis import static_vals as astatic

VALIDATE_MSG_ZERO_OR_GREATER = 'The value must be a number, zero or greater.'
VALIDATE_MSG_ONE_OR_GREATER = 'The value must be a number, 1 or greater.'
VALIDATE_MSG_EPSILON = 'As a rule of thumb, epsilon should not be less than 0.001 nor greater than 1.'
VALIDATE_MSG_NOT_FLOAT = 'The value must be a float.'
VALIDATE_MSG_NOT_INT = 'The value must be an integer.'
VALIDATE_MSG_NOT_VALID_CI = 'Valid confidence interval values:'
VALIDATE_MSG_UNSUPPORTED_STATISTIC = 'Valid statistics:'

def validate_statistic(value):
    """Statistic currently supported"""
    if not value in astatic.DP_STATS_CHOICES:
        ci_choices_str = ', '.join(astatic.DP_STATS_CHOICES)
        user_msg = f'{VALIDATE_MSG_UNSUPPORTED_STATISTIC} {ci_choices_str}'
        raise ValidationError(user_msg)

def validate_confidence_interval(value):
    """Validate a valid CI"""
    validate_float(value)
    #
    ci_choices = [x[0] for x in astatic.CI_CHOICES]
    if not value in ci_choices:
        ci_choices_str = ', '.join([str(x) for x in ci_choices])
        user_msg = f'{VALIDATE_MSG_NOT_VALID_CI} {ci_choices_str}'
        raise ValidationError(user_msg)

def validate_not_negative(value):
    """Valid values are non-negative numbers"""
    if value < 0.0:
        raise ValidationError(VALIDATE_MSG_ZERO_OR_GREATER)

def validate_int_greater_than_zero(value):
    """Validate int greater >= 1"""
    if not isinstance(value, int):
        raise ValidationError(VALIDATE_MSG_NOT_INT)

    if value < 1:
        raise ValidationError(VALIDATE_MSG_ONE_OR_GREATER)


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

    if not value:
        raise ValidationError('The value cannot be empty.')

def validate_epsilon_not_null(value):
    """
    As a rule of thumb, however, epsilon should be thought of as a small number,
    between approximately  1/100 and 1
    source: https://admindatahandbook.mit.edu/book/v1.0/diffpriv.html
    """
    validate_float(value)

    if value > 1 or value < 0.01:
        raise ValidationError(VALIDATE_MSG_EPSILON)



def validate_float(value):
    """Make sure the value is a float"""
    try:
        float(value)
    except ValueError:
        raise ValidationError(VALIDATE_MSG_NOT_FLOAT)

"""
from opendp_apps.utils.extra_validators import *

try:
    validate_not_negative_or_none(-0.3)
except ValidationError as err_obj:
    err_obj.messages
    err_obj.message
"""