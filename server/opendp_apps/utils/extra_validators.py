from django.core.exceptions import ValidationError

VALIDATE_MSG_ZERO_OR_GREATER = 'The value must be a number, zero or greater.'
VALIDATE_MSG_EPSILON = 'As a rule of thumb, epsilon should not be less than 0.001 nor greater than 1.'
VALIDATE_MSG_NOT_FLOAT = 'The value must be a float.'

def validate_not_negative(value):
    """Valid values are non-negative numbers"""
    if value < 0.0:
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