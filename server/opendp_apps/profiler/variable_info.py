"""
Profile a data file
"""
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck


class VariableInfoHandler(BasicErrCheck):

    def __init__(self, df):
        """
        Given a dataframe, create a variable profile dictionary
        :param df: Dataframe
        """
        self.df = df

    def run_profile_process(self):
        profile_dict = {}
        num_rows, num_variables = self.df.shape
        profile_dict['rowCount'] = num_rows
        profile_dict['variableCount'] = num_variables
        variable_order = [(i, x) for i, x in enumerate(self.df.columns)]
        profile_dict['variableOrder'] = variable_order
        profile_dict['variables'] = []
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
                column_info['min'] = column.min()
                column_info['max'] = column.max()
            profile_dict['variables'].append({
                col_name: column_info
            })
        return profile_dict
