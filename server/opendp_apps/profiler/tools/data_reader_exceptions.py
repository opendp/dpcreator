class DelimiterNotFoundException(Exception):
    """
    This exception should be raised when a file does not have a clear
    delimiter (empty, corrupted, etc.)
    """
    pass


class ColumnLimitInvalid(Exception):
    """
    The column limit may be None or an integer > 0
    """
    pass


class InvalidFileType(Exception):
    """
    A file type was passed that cannot be processed by the given data reader
    """
    pass
