import os

import pyreadstat

from opendp_apps.profiler.tools.base_data_reader import BaseDataReader
from opendp_apps.profiler.tools.data_reader_exceptions import InvalidFileType


class SpssReader(BaseDataReader):

    def __init__(self, filepath, column_limit=None):
        self.meta = None
        super().__init__(filepath=filepath, column_limit=column_limit)

    def read(self):
        file_name, extension = os.path.splitext(self.filepath)
        if extension == '.sav':
            df, meta = pyreadstat.read_sav(self.filepath)
        elif extension == '.dta':
            df, meta = pyreadstat.read_dta(self.filepath)
        else:
            raise InvalidFileType(f"The file type {extension} is not supported by SpssReader")
        if self.column_limit:
            df = df[df.columns[:self.column_limit]]
        self.meta = meta
        return df


if __name__ == '__main__':
    reader = SpssReader('server/opendp_apps/profiler/testing/golf.dta', 20)
    print(reader.read())