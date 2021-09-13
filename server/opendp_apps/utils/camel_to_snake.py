"""
Utility function
"""
import re

def camel_to_snake(name):
    """
    Front end is passing camelCase, but JSON in DB is using snake_case
    :param name:
    :return:
    """
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
