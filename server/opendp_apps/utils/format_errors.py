"""
Shortcut for formatting serializer.errors
"""

def format_serializer_errors(serializer_errors: dict) -> dict:
    """
    Format the errors for easier use, converting the ErrorDetail object into a string by using 'title()'
    """
    formatted_errors = {}
    for field_name, err_detail in serializer_errors.items():
        formatted_errors[field_name] = str(err_detail[0])

    return formatted_errors
