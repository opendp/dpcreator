from django.conf import settings
import csv
import pandas as pd


class DelimiterNotFoundException(Exception):
    """
    This exception should be raised when a file does not have a clear
    delimiter (empty, corrupted, etc.)
    """
    pass

class ColumnLimitLessThanOne(Exception):
    """
    This exception should be raised when the column limit is less than 1
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
        if not self.column_limit:
            self.column_limit = settings.PROFILER_COLUMN_LIMIT

        if self.column_limit < 1:
            raise ColumnLimitLessThanOne()

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
        except UnicodeDecodeError as ex:
            raise ex
        except csv.Error as ex:
            if self.delimiter is None:
                raise DelimiterNotFoundException()
            raise ex
