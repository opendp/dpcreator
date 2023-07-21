"""
Validators used by DatasetInfo fields
"""
from django.core.exceptions import ValidationError
from typing import Union

from opendp_apps.analysis import static_vals as astatic


def validate_dataset_questions(value: Union[dict, None, str], to_set_user_step=False):
    """
    Check that the dataset_questions, if specified, are valid
    """
    # blank/null values are okay
    if not value:
        return

    # Is it a dict?
    if not isinstance(value, dict):
        raise ValidationError(astatic.ERR_MSG_DATASET_QUESTIONS_NOT_DICT)

    question_keys = astatic.SETUP_QUESTION_LOOKUP.keys()
    for qkey, qval in value.items():
        # Is the question key valid?
        if qkey not in question_keys:
            raise ValidationError(astatic.ERR_MSG_DATASET_QUESTIONS_INVALID_KEY.format(key=qkey))

        # Allow empty strings for API calls, but not for setting the user step on save
        if to_set_user_step is True:
            pass
        elif qval == "":
            continue

        if qkey == astatic.SETUP_Q_02_ATTR:
            if not qval in astatic.SETUP_Q_02_CHOICES:
                _err_msg = astatic.ERR_MSG_DATASET_QUESTIONS_INVALID_VALUE.format(key=qkey, value=qval)
                raise ValidationError(_err_msg)

        if qkey in astatic.YES_NO_QUESTIONS:
            if qval not in astatic.YES_NO_VALUES:
                _err_msg = astatic.ERR_MSG_DATASET_YES_NO_QUESTIONS_INVALID_VALUE.format(key=qkey, value=qval)
                raise ValidationError(_err_msg)

    return


def validate_epsilon_questions(value: Union[dict, None, str], to_set_user_step=False):
    """
    Check that the object_id belongs to an existing DatasetInfo object
    @param value: dict of epsilon questions
    @param to_set_user_step: boolean, if True, then values may not include empty strings

    """
    # blank/null values are okay
    # print('>>> validate_epsilon_questions', value)
    if not value:
        return None

    # Is it a dict?
    if not isinstance(value, dict):
        raise ValidationError(astatic.ERR_MSG_DATASET_QUESTIONS_NOT_DICT)

    question_keys = astatic.EPSILON_QUESTION_LIST
    for qkey, qval in value.items():
        # Is the question key valid?
        if qkey not in question_keys:
            raise ValidationError(astatic.ERR_MSG_DATASET_QUESTIONS_INVALID_KEY.format(key=qkey))

        # Allow empty strings for API calls, but not for setting the user step on save
        if to_set_user_step is True:
            pass
        elif qval == "":
            continue

        # Is the question #4 yes?
        if qkey == astatic.SETUP_Q_04_ATTR and qval == astatic.YES_VALUE:
            if not astatic.SETUP_Q_04a_ATTR in value:
                _err_msg = astatic.ERR_MSG_POPULATION_SIZE_MISSING.format(pop_size=None)
                raise ValidationError(_err_msg)

            pop_size = value.get(astatic.SETUP_Q_04a_ATTR)
            if pop_size:
                if not isinstance(value.get(astatic.SETUP_Q_04a_ATTR), int):
                    _err_msg = astatic.ERR_MSG_POPULATION_SIZE_MISSING.format(val_type=type(pop_size))
                    raise ValidationError(_err_msg)
                elif pop_size < 1:
                    _err_msg = astatic.ERR_MSG_POPULATION_CANNOT_BE_NEGATIVE.format(pop_size=pop_size)
                    raise ValidationError(_err_msg)

        if qkey in astatic.YES_NO_QUESTIONS:
            if qval not in astatic.YES_NO_VALUES:
                _err_msg = astatic.ERR_MSG_DATASET_YES_NO_QUESTIONS_INVALID_VALUE.format(key=qkey, value=qval)
                raise ValidationError(_err_msg)

    return