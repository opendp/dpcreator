from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler.tools.data_reader_exceptions import ColumnLimitInvalid


class BaseDataReader(object):

    def __init__(self, filepath, column_limit=None):
        """
        Utility for reading a delimited file into a dataframe,
        with automatic delimiter detection
        :param filepath: File to read from
        :param column_limit: If passed, only return the first N columns in the dataframe
        """
        self.filepath = filepath
        self.delimiter = None

        self.column_limit = column_limit

        if self.column_limit is not None:
            if not isinstance(self.column_limit, int):
                raise ColumnLimitInvalid(f'{pstatic.ERR_MSG_COLUMN_LIMIT} Found: "{self.column_limit}"')
            if self.column_limit < 1:
                raise ColumnLimitInvalid(f'{pstatic.ERR_MSG_COLUMN_LIMIT} Found: "{self.column_limit}"')

    def read(self, *args, **kwargs):
        raise NotImplementedError
