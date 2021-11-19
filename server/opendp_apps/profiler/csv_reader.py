import csv
import pandas as pd


class DelimiterNotFoundException(Exception):
    pass


class CsvReader:

    def __init__(self, filepath, column_limit=None):
        self.filepath = filepath
        self.delimiter = None
        self.column_limit = column_limit

    def read(self):
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

