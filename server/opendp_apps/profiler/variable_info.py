"""
Profile a data file
"""
import numpy as np

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.profiler.csv_reader import CsvReader
from opendp_apps.profiler.static_vals import VAR_TYPE_INTEGER, VAR_TYPE_BOOLEAN, VAR_TYPE_FLOAT, VAR_TYPE_CATEGORICAL, \
    VAR_TYPE_NUMERICAL


class EmptyDataframeException(Exception):
    pass


class VariableInfoHandler(BasicErrCheck):

    def __init__(self, df):
        """
        Given a dataframe, create a variable profile dictionary
        :param df: Dataframe
        """
        self.df = df
        self.num_original_features = df.shape[1]
        self.data_profile = None

    def run_profile_process(self):
        profile_dict = {'dataset': {}}
        num_rows, num_variables = self.df.shape
        profile_dict['dataset']['rowCount'] = int(num_rows)
        profile_dict['dataset']['variableCount'] = int(num_variables)
        variable_order = [(i, x) for i, x in enumerate(self.df.columns)]
        profile_dict['dataset']['variableOrder'] = variable_order
        profile_dict['variables'] = {}
        for col_name in self.df.columns:
            column = self.df[col_name]
            column_info = {
                "name": col_name,
                "label": ""
            }
            # category_limit = 5
            # Use type checking to filter out numpy Nan
            # Comment out categories for now
            if column.unique().shape[0] == 2:
                column_info['categories'] = []
                column_info['type'] = VAR_TYPE_BOOLEAN
            elif str(column.dtypes) == 'object':
                column_info['categories'] = []  #  list([x for x in column.unique() if type(x) == str])[:category_limit]
                column_info['type'] = VAR_TYPE_CATEGORICAL
            elif hasattr(column.dtypes, 'categories'):
                column_info['categories'] = []  # list([x for x in column.dtypes.categories if type(x) == str])[:category_limit]
                column_info['type'] = VAR_TYPE_CATEGORICAL
            elif 'int' in str(column.dtype):
                column_info['min'] = int(column.min()) if not np.isnan(column.min()) else None
                column_info['max'] = int(column.max()) if not np.isnan(column.max()) else None
                column_info['type'] = VAR_TYPE_NUMERICAL
            elif 'float' in str(column.dtype):
                column_info['min'] = float(column.min()) if not np.isnan(column.min()) else None
                column_info['max'] = float(column.max()) if not np.isnan(column.max()) else None
                column_info['type'] = VAR_TYPE_NUMERICAL
            elif str(column.dtypes) != 'object':
                column_info['min'] = float(column.min()) if not np.isnan(column.min()) else None
                column_info['max'] = float(column.max()) if not np.isnan(column.max()) else None
                column_info['type'] = VAR_TYPE_NUMERICAL
            profile_dict['variables'][col_name] = column_info

        self.data_profile = profile_dict
        return profile_dict


if __name__ == '__main__':
    csv_reader = CsvReader('/Users/ethancowan/IdeaProjects/opendp-ux/server/test_data/voter_validation_lwd.csv')
    df = csv_reader.read()
    v = VariableInfoHandler(df)
    profile_dict = v.run_profile_process()
    from pprint import pprint
    pprint(profile_dict)