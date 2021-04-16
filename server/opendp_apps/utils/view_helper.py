"""
Utilities for views
"""
from collections import OrderedDict

from rest_framework.exceptions import APIException, ParseError
from rest_framework.views import exception_handler


def get_json_error(err_msg, errors=None):
    """return an OrderedDict with success=False + message"""
    info = OrderedDict()
    info['success'] = False
    info['message'] = err_msg
    if errors:
        info['errors'] = errors
    return info


def get_json_success(user_msg, **kwargs):
    """return an OrderedDict with success=True + message + optional 'data'"""
    info = OrderedDict()
    info['success'] = True
    info['message'] = user_msg

    if 'data' in kwargs:
        info['data'] = kwargs['data']

    # add on additional data pieces
    for key, val in kwargs.items():
        if key == 'data':
            continue
        info[key] = val

    return info


class ExceptionResponse(APIException):

    def __init__(self, body, status, *args, **kwargs):
        self.body = body
        self.status = status
        super(ExceptionResponse, self).__init__(*args, **kwargs)


def opendp_exception_handler(exc, context):
    """
    Custom exception handler. Set in REST_FRAMEWORK in settings.py
    Currently not modifying anything.
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    # if response is not None:
    #     response.data['status_code'] = response.status_code
    return response


def get_object_or_error_response(model, **kwargs):
    """
    Utility to find the object for the given model
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:

        # This could lead to other errors with split() and replace()
        # if string isn't formatted as expected:
        model_type = repr(model).split('.')[-1].replace('>', '').replace('\'', '')

        # Alternatively, format model type this way,
        # model_type = repr(model)
        # but this shows full classpath to frontend
        response = ParseError(detail={'success': False, 'message': f'{model_type} not found'})
        raise response
