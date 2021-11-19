import csv
import pandas as pd


class DelimiterNotFoundException(Exception):
    """
    This exception should be raised when a file does not have a clear
    delimiter (empty, corrupted, etc.)
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
            df = pd.read_csv(self.filepath, self.delimiter)
            if self.column_limit:
                return df[df.columns[:self.column_limit]]
            return df
        except UnicodeDecodeError as ex:
            raise ex
        except csv.Error as ex:
            if self.delimiter is None:
                raise DelimiterNotFoundException()
            raise ex
