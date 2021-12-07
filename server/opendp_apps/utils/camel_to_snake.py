"""
Utility function
"""
import re

RE_REMOVE_SPACE = re.compile(r"\s+")
RE_CAMEL_TO_SNAME = re.compile(r'(?<!^)(?=[A-Z])')

def camel_to_snake(name: str) -> str:
    """
    Front end is passing camelCase, but JSON in DB is using snake_case
    :param name:
    :return:
    """
    name = RE_REMOVE_SPACE.sub('', name)
    #
    return RE_CAMEL_TO_SNAME.sub('_', name).lower()
    #
    # return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
