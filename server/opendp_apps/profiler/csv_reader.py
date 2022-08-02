import csv

import pandas as pd

from opendp_apps.profiler import static_vals as pstatic


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


class CsvReader:

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

    def read(self):
        """
        Build the dataframe
        :return: pd.DataFrame
        """
        sniffer = csv.Sniffer()
        try:
            with open(self.filepath, mode='r', encoding='utf-8') as infile:
                dialect = sniffer.sniff(infile.readline())
                self.delimiter = dialect.delimiter
            df = pd.read_csv(self.filepath, delimiter=self.delimiter)
            if self.column_limit:
                return df[df.columns[:self.column_limit]]
            return df
        except pd.errors.EmptyDataError as err_obj:
            user_msg = f'{pstatic.ERR_FAILED_TO_READ_DATASET} (EmptyDataError: {err_obj})'
            return err_resp(user_msg)
        except pd.errors.ParserError as err_obj:
            user_msg = f'{pstatic.ERR_FAILED_TO_READ_DATASET} (ParserError: {err_obj})'
            return err_resp(user_msg)
        except UnicodeDecodeError as ex:
            raise ex
        except csv.Error as ex:
            if self.delimiter is None:
                raise DelimiterNotFoundException()
            raise ex
