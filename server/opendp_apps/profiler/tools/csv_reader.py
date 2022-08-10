import csv

import pandas as pd
from pandas.errors import EmptyDataError

from opendp_apps.model_helpers.basic_response import err_resp
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler.tools.base_data_reader import BaseDataReader
from opendp_apps.profiler.tools.data_reader_exceptions import DelimiterNotFoundException


class CsvReader(BaseDataReader):

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
