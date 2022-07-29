"""
Profile a data file
"""
from collections import OrderedDict

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.profiler.tools.csv_reader import CsvReader
from opendp_apps.profiler.static_vals import \
    (KEY_SAVE_ROW_COUNT,
     VAR_TYPE_BOOLEAN,
     VAR_TYPE_CATEGORICAL,
     VAR_TYPE_FLOAT,
     VAR_TYPE_INTEGER,
     VAR_TYPE_NUMERICAL)


class VariableInfoHandler(BasicErrCheck):

    def __init__(self, df, **kwargs):
        """
        Given a dataframe, create a variable profile dictionary
        :param df: Dataframe
        """
        self.df = df
        self.num_variables = None
        self.data_profile = None

        self.save_num_rows = kwargs.get(KEY_SAVE_ROW_COUNT, True)

    def run_profile_process(self):
        """
        Process the dataframe into a complete data profile dictionary
        :return:
        {
            'dataset': {
                'rowCount': 1500,
                'variableCount': 132,
                'variableOrder': [(0, 'some_column'), ....]
            },
            'variables': {
                'some_column': {
                    'label': '',
                    'name': 'some_column',
                    'type': 'Categorical'
                }
            }
        }
        """
        profile_dict = {'dataset': {}}
        num_rows, self.num_variables = self.df.shape
        if self.save_num_rows is True:
            profile_dict['dataset']['rowCount'] = int(num_rows)
        else:
            profile_dict['dataset']['rowCount'] = None

        profile_dict['dataset']['variableCount'] = int(self.num_variables)
        variable_order = [(i, x) for i, x in enumerate(self.df.columns)]
        profile_dict['dataset']['variableOrder'] = variable_order
        profile_dict['variables'] = {}

        sort_order = -1
        for col_name in self.df.columns:
            sort_order += 1
            column = self.df[col_name]
            column_info = OrderedDict({
                "name": col_name,
                "sort_order": sort_order,
                "label": ""
            })
            # category_limit = 5
            # Use type checking to filter out numpy Nan
            # Comment out categories for now
            if column.unique().shape[0] == 2:
                column_info['categories'] = []
                column_info['type'] = VAR_TYPE_BOOLEAN
            elif str(column.dtypes) == 'object':
                column_info['categories'] = []  # list([x for x in column.unique() if type(x) == str])[:category_limit]
                column_info['type'] = VAR_TYPE_CATEGORICAL
            elif hasattr(column.dtypes, 'categories'):
                column_info['categories'] = []  # list([x for x in column.dtypes.categories if type(x) == str])[:category_limit]
                column_info['type'] = VAR_TYPE_CATEGORICAL
            elif 'int' in str(column.dtype):
                # column_info['min'] = int(column.min()) if not np.isnan(column.min()) else None
                # column_info['max'] = int(column.max()) if not np.isnan(column.max()) else None
                column_info['type'] = VAR_TYPE_INTEGER
            elif 'float' in str(column.dtype):
                # column_info['min'] = float(column.min()) if not np.isnan(column.min()) else None
                # column_info['max'] = float(column.max()) if not np.isnan(column.max()) else None
                column_info['type'] = VAR_TYPE_FLOAT
            elif str(column.dtypes) != 'object':
                # column_info['min'] = float(column.min()) if not np.isnan(column.min()) else None
                # column_info['max'] = float(column.max()) if not np.isnan(column.max()) else None
                column_info['type'] = VAR_TYPE_NUMERICAL
            profile_dict['variables'][col_name] = column_info

        self.data_profile = profile_dict
        return profile_dict


if __name__ == '__main__':
    import os
    from pprint import pprint
    from server.opendp_project.settings.base import BASE_DIR

    fname = 'Fatigue_data.tab'
    # fname = 'teacher_climate_survey_lwd.csv'
    csv_reader = CsvReader(os.path.join(BASE_DIR, 'test_data' , 'teacher_climate_survey_lwd.csv'))
    df = csv_reader.read()
    v = VariableInfoHandler(df)
    profile_dict = v.run_profile_process()
    pprint(profile_dict)
