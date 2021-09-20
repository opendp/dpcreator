"""
Convenience methods to format the output of the PreprocessRunner
    (e.g. from raven_preprocess.preprocess_runner import PreprocessRunner)

"""
from collections import OrderedDict
from opendp_apps.model_helpers.basic_response import BasicResponse, ok_resp, err_resp
from opendp_apps.profiler import static_vals as pstatic


class ProfileFormatter:

    @staticmethod
    def prune_profile(profile_data: dict, save_row_count: bool=True) -> BasicResponse:
        """Remove fields from the output of the TwoRavens preprocesser"""
        if not isinstance(profile_data, dict):
            user_msg = 'The data profile must be a Python dict.'
            return err_resp(user_msg)

        if not 'variables' in profile_data:
            user_msg = 'The profile_data must contain the key "variables"'
            return err_resp(user_msg)

        if 'variableDisplay' in profile_data:
            del profile_data['variableDisplay']

        # Remove everything from the "dataset" field, except "variableCount", "variableOrder"
        #   and (sometimes) "rowCount" move it to the top level
        #
        if 'dataset' in profile_data:
            features_to_keep = [ "variableCount", "variableOrder"]
            features_to_nullify = []
            if save_row_count is True:
                features_to_keep.append('rowCount')
            else:
                features_to_nullify.append('rowCount')

            features_to_del = []

            for key in profile_data['dataset']:
                if not key in features_to_keep:
                    if key in features_to_nullify:
                        profile_data['dataset'][key] = None
                    else:
                        features_to_del.append(key)

            for del_key in features_to_del:
                del profile_data['dataset'][del_key]

        # Prune variables, keeping only these:
        #
        var_keys_to_keep = ['variableName', 'description',
                            'numchar', 'nature', 'binary', 'interval',
                            #'geogrphic', 'temporal',
                            #'invalidCount', 'validCount', 'uniqueCount'
                            ]

        # Gather all the variable names
        var_names = profile_data['variables'].keys()

        # Iterate through the profile and remove unnecessary keys
        #
        for vname in var_names:
            var_all_keys = profile_data['variables'][vname].keys()

            # list of un-needed keys
            keys_to_remove = [x for x in var_all_keys
                              if not x in var_keys_to_keep]

            # delete un-needed keys
            for del_key in keys_to_remove:
                del profile_data['variables'][vname][del_key]

        return ok_resp(profile_data)

    @staticmethod
    def format_profile_variables(profile_data: dict) -> BasicResponse:
        """Format the output of "prune_profile, determining the variable type"""
        #import json; print('profile_data', json.dumps(profile_data))
        if not isinstance(profile_data, dict):
            user_msg = 'The data profile must be a Python dict.'
            return err_resp(user_msg)

        if not 'variables' in profile_data:
            user_msg = 'The profile_data must contain the key "variables"'
            return err_resp(user_msg)

        if not 'dataset' in profile_data:
            user_msg = 'The profile_data must contain the key "dataset"'
            return err_resp(user_msg)


        # ------------------------------------------------
        # Iterate through the variables and format them
        # ------------------------------------------------

        # Get the variable names!
        #
        var_names = profile_data['variables'].keys()

        # Create OrderedDict to hold the formatted profile
        #
        profile_formatted = OrderedDict([('dataset', profile_data['dataset']),])
        profile_variables = OrderedDict()

        # Iterate through the variables
        #
        for vname in var_names:
            # Get variable info
            #
            orig_var_info = profile_data['variables'][vname]

            # Check that variable has necessary fields
            #
            expected_fields = ('variableName', 'description', 'binary', 'numchar', 'interval')
            for ef in expected_fields:
                if not ef in orig_var_info:
                    user_msg = (f'Profile for variable "{vname}" does not have'
                                f' expected field "{ef}".')
                    return err_resp(user_msg)

            # Determine the variable type
            #   - possible types: boolean, numerical, categorical
            #
            if orig_var_info['binary'] is True:
                var_type = pstatic.VAR_TYPE_BOOLEAN
            elif orig_var_info['numchar'] == 'numeric':
                var_type = pstatic.VAR_TYPE_NUMERICAL
                # if orig_var_info['interval'] == 'continuous': # currently unused
            else:
                var_type = pstatic.VAR_TYPE_CATEGORICAL

            # Add formatted variable info to formatted profile
            #
            fmt_var_info = [('name', orig_var_info['variableName']),
                            ('label', orig_var_info['description']),
                            ('type', var_type),]

            # Depending on the variable type, add additional variables
            #
            if var_type == pstatic.VAR_TYPE_NUMERICAL:
                fmt_var_info.append(('min', None))
                fmt_var_info.append(('max', None))
            elif var_type == pstatic.VAR_TYPE_CATEGORICAL:
                fmt_var_info.append(('categories', None))

            profile_variables[vname] = OrderedDict(fmt_var_info)

        profile_formatted['variables'] = profile_variables

        #import json; print('profile_formatted', json.dumps(profile_formatted, indent=4))

        return ok_resp(profile_formatted)