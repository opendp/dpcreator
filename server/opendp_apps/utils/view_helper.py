"""
Utilities for views
"""
from collections import OrderedDict


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
