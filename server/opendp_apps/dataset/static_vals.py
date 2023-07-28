ERR_MSG_DATASET_INFO_NOT_FOUND = 'DatasetInfo object not found'
ERR_MSG_INVALID_DATASET_INFO_OBJECT_ID = 'Invalid DatasetInfo object id.'

ERR_MSG_DATASET_INFO_NOT_FOUND_CURRENT_USER = ('DatasetInfo object not found'
                                               ' for the current user.')

ERR_MSG_FAILED_TO_READ_DATASET = 'Failed to read the dataset.'
ERR_MSG_DATASET_POINTER_NOT_SET = 'In order to profile the data, the "dataset_pointer" must be set.'

ERR_MSG_DATASET_LOCKED_BY_ANOTHER_USER = 'This Dataverse file is locked by another user.'
ERR_MSG_NO_VARIABLE_INFO = 'No variable info found for this dataset.'
ERR_MSG_NO_VARIABLES_SELECTED = 'None of the variables in this "variable_info" were selected.'

MSG_VAL_NOT_SPECIFIED = '(not specified)'

KEY_WIZARD_STEP = 'wizard_step'
WIZARD_STEP_DEFAULT_VAL = 'step_100'

ERR_MSG_COMPLETE_NOT_ALLOWED_INVALID_DATA = (' The "is_complete" field may only be set to True until'
                                             ' other setup data has been entered.')

ERR_MSG_ONLY_WIZARD_ALREADY_COMPLETE = (f'The DepositorSetupInfo is complete. Only the'
                                           f' "{KEY_WIZARD_STEP}" may be updated.')

ERR_MSG_ONLY_WIZARD_STEP_MAY_BE_UPDATED = ('When updating the field "is_complete", the only other field'
                                           ' that may be updated is "wizard_step". The request'
                                           ' attempted to update: {key_list_str}')