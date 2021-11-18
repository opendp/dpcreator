"""
Profile a data file
"""
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck


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
                "type": str(column.dtype),
                "label": ""
            }
            if str(column.dtypes) == 'object':
                column_info['categories'] = list(column.unique())
                column_info['type'] = 'categorical'
            elif hasattr(column.dtypes, 'categories'):
                column_info['categories'] = list(column.dtypes.categories)
                column_info['type'] = 'categorical'
            elif str(column.dtypes) != 'object':
                column_info['min'] = float(column.min())
                column_info['max'] = float(column.max())
            profile_dict['variables'][col_name] = column_info

        self.data_profile = profile_dict
        return profile_dict
