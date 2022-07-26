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
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    name = re.sub('__([A-Z])', r'_\1', name)
    name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
    return name.lower()
