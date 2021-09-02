from django.core.exceptions import ValidationError

VALIDATE_MSG_ZERO_OR_GREATER = 'The value must be a number, zero or greater.'

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