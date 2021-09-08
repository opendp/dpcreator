from django.core.exceptions import ValidationError

VALIDATE_MSG_ZERO_OR_GREATER = 'The value must be a number, zero or greater.'
VALIDATE_MSG_EPSILON = 'As a rule of thumb, epsilon should not be less than 0.001 nor greater than 1.'

def validate_not_negative(value):
    """Valid values are non-negative numbers"""
    if value < 0.0:
        raise ValidationError(VALIDATE_MSG_ZERO_OR_GREATER)


def validate_not_negative_or_none(value):
    """Valid values are None or non-negative numbers"""
    if value is None:
        # okay value!
        return

    return validate_not_negative(value)

def validate_epsilon_or_none(value):
    """
    As a rule of thumb, however, epsilon should be thought of as a small number,
    between approximately  1/100 and 1
    source: https://admindatahandbook.mit.edu/book/v1.0/diffpriv.html
    """
    if value is None:
        # okay value!
        return

    if value > 1 or value < 0.01:
        raise ValidationError(VALIDATE_MSG_EPSILON)