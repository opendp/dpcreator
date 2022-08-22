# keyword param for the ProfileHandler
KEY_DATASET_OBJECT_ID = 'dataset_object_id'
KEY_SAVE_ROW_COUNT = 'save_row_count'
KEY_DATASET_IS_DJANGO_FILEFIELD = 'dataset_is_django_filefield'
KEY_DATASET_IS_FILEPATH = 'dataset_is_filepath'

VAR_TYPE_BOOLEAN = 'Boolean'
VAR_TYPE_CATEGORICAL = 'Categorical'
VAR_TYPE_NUMERICAL = 'Numerical'
VAR_TYPE_INTEGER = 'Integer'
VAR_TYPE_FLOAT = 'Float'

NUMERIC_VAR_TYPES = [VAR_TYPE_NUMERICAL, VAR_TYPE_INTEGER, VAR_TYPE_FLOAT]

VALID_VAR_TYPES = [VAR_TYPE_BOOLEAN,
                   VAR_TYPE_CATEGORICAL,
                   VAR_TYPE_NUMERICAL,
                   VAR_TYPE_INTEGER,
                   VAR_TYPE_FLOAT]

KW_MAX_NUM_FEATURES = 'max_num_features'

# -----------------------------

ERR_MSG_VAR_TYPE_NOT_NUMERIC = 'The variable type must be one of the following: %s' % (', '.join(NUMERIC_VAR_TYPES))
ERR_MSG_VAR_TYPE_NOT_CATEGORICAL = f'The variable type must be: {VAR_TYPE_CATEGORICAL}'
ERR_MSG_COLUMN_LIMIT = 'The column_limit may be "None" or an integer greater than 0.'
ERR_MSG_SOURCE_FILE_DOES_NOT_EXIST = 'The source file does not exist for dataset: '
ERR_MSG_DATASET_POINTER_NOT_FIELDFILE = 'The dataset pointer is not a Django FieldFile object.'

ERR_FAILED_TO_READ_DATASET = 'Failed to read the dataset.'
ERR_DATASET_POINTER_NOT_SET = 'In order to profile the data, the "dataset_pointer" must be set.'
