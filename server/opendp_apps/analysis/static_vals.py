NOISE_GEOMETRIC_MECHANISM = 'Geometric'
NOISE_LAPLACE_MECHANISM = 'Laplace'

"""
Epsilon related values
As a rule of thumb, Epsilon should be thought of as a small number, between approximately 1/1000
and 1.

When checking max_epsilon, offset it by 10**-14 to avoid
  floating point addition issues. e.g. exceeding an espilon of 1 by: 0.0000000000000001
"""
MAX_EPSILON_OFFSET = 10 ** -14

# ---------------------------------
# Confidence level static values
# ---------------------------------
CL_90 = 0.90  # just to look at
CL_95 = 0.95
CL_99 = 0.99

CL_90_ALPHA = 0.10
CL_95_ALPHA = 0.05
CL_99_ALPHA = 0.01

CL_CHOICES = (
    (CL_90, '90% CL'),
    (CL_95, '95% CL'),
    (CL_99, '99% CL'),
)

# --------------------------------------
# Often-used Delta values
# --------------------------------------
DELTA_0 = 0.0
DELTA_10_NEG_5 = 10.0 ** -5
DELTA_10_NEG_6 = 10.0 ** -6
DELTA_10_NEG_7 = 10.0 ** -7

# --------------------------------------
# Statistic Types
# --------------------------------------
DP_MEAN = 'mean'
DP_SUM = 'sum'
DP_COUNT = 'count'
DP_HISTOGRAM = 'histogram'
DP_HISTOGRAM_CATEGORICAL = 'histogram_categorical'
DP_HISTOGRAM_INTEGER = 'histogram_integer'
DP_QUANTILE = 'quantile'
DP_VARIANCE = 'variance'
DP_STATS_CHOICES = [DP_COUNT,
                    DP_HISTOGRAM,
                    DP_MEAN,
                    DP_QUANTILE,
                    DP_SUM,
                    # DP_HISTOGRAM_CATEGORICAL,
                    # DP_HISTOGRAM_INTEGER,
                    DP_VARIANCE]

DP_STATS_REQUIRE_COUNTS = [DP_MEAN,
                           DP_SUM,
                           DP_QUANTILE,
                           DP_VARIANCE]

VALID_DP_STATS_CHOICES_STR = ', '.join(DP_STATS_CHOICES)

# --------------------------------------
# Keys (mostly Histogram bin types)
# --------------------------------------
KEY_VARIABLE_INFO = 'variable_info'

KEY_HIST_BIN_TYPE = 'histogram_bin_type'
KEY_HIST_NUMBER_OF_BINS = 'histogram_number_of_bins'
KEY_HIST_BIN_EDGES = 'histogram_bin_edges'

HIST_BIN_TYPE_BOOLEAN = 'binTypeBoolean'
HIST_BIN_TYPE_ONE_PER_VALUE = 'onePerValue'
HIST_BIN_TYPE_EQUAL_RANGES = 'equalRanges'
HIST_BIN_TYPE_BIN_EDGES = 'binEdges'
HIST_VALID_BIN_TYPES = [HIST_BIN_TYPE_BOOLEAN,
                        HIST_BIN_TYPE_ONE_PER_VALUE,
                        HIST_BIN_TYPE_EQUAL_RANGES,
                        HIST_BIN_TYPE_BIN_EDGES]
VALID_HIST_BIN_TYPE_CHOICES_STR = ', '.join(HIST_VALID_BIN_TYPES)
ERR_MSG_HIST_BIN_TYPE_UKNOWN = (f'Unknown histogram bin type. Expected:'
                                f' {VALID_HIST_BIN_TYPE_CHOICES_STR}')
ERR_MSG_TOO_MANY_BINS = 'There are too many bins given the min and max values.'
# --------------------------------------
# Missing value handling
# --------------------------------------
KEY_MISSING_VALUES_HANDLING = 'missing_values_handling'
KEY_FIXED_VALUE = 'fixed_value'
KEY_AUTO_GENERATED_DP_COUNT = 'auto_generated_dp_count'

MISSING_VAL_DROP = 'drop'
MISSING_VAL_INSERT_RANDOM = 'insert_random'
MISSING_VAL_INSERT_FIXED = 'insert_fixed'
MISSING_VAL_NOT_APPLICABLE = ''

MISSING_VAL_HANDLING_TYPES = [MISSING_VAL_DROP,
                              MISSING_VAL_INSERT_RANDOM,
                              MISSING_VAL_INSERT_FIXED,
                              MISSING_VAL_NOT_APPLICABLE]

MISSING_VAL_HANDING_LABELS = {
    MISSING_VAL_DROP: "Drop Missing Value",
    MISSING_VAL_INSERT_RANDOM: "Insert Random Value",
    MISSING_VAL_INSERT_FIXED: "Insert Fixed Value",
    MISSING_VAL_NOT_APPLICABLE: "Not applicable",
}


def missing_val_label(missing_val_type):
    assert missing_val_type in MISSING_VAL_HANDING_LABELS, \
        f"The type of missing value is unknown! {missing_val_type}"
    return MISSING_VAL_HANDING_LABELS.get(missing_val_type)


# --------------------------------------
# Error Messages
# --------------------------------------
ERR_MSG_ANALYSIS_PLAN_NOT_FOUND = 'The AnalysisPlan was not found.'

ERR_MSG_DATASET_ID_REQUIRED = 'The DataSetInfo id is required.'
ERR_MSG_ANALYSIS_ID_REQUIRED = 'The AnalysisPlan id is required.'

ERR_MSG_USER_REQUIRED = 'The OpenDP user is required.'
ERR_MSG_NO_DATASET = 'DataSetInfo object not found for this object_id and creator'
ERR_MSG_SETUP_INCOMPLETE = 'Depositor setup is not complete'

ERR_MSG_NO_ANALYSIS_PLAN = 'AnalysisPlan object not found for this object_id and creator'
ERR_MSG_FIELDS_NOT_UPDATEABLE = 'These fields are not updatable'

ERR_MSG_BAD_TOTAL_EPSILON = 'The depositor setup info has an invalid epsilon value'
ERR_MSG_BAD_TOTAL_DELTA = 'The depositor setup info has an invalid delta value'

ERR_MSG_INVALID_MIN_MAX = 'The "max" must be greater than the "min"'

ERR_IMPUTE_PHRASE_MIN = 'cannot be less than the "min"'
ERR_IMPUTE_PHRASE_MAX = 'cannot be more than the "max"'

ERR_MAX_NOT_GREATER_THAN_MIN = 'The max must be greater than the min.'

ERR_MSG_CL_ALPHA_CL_NOT_SET = 'Attempted to calculate confidence level (CL) alpha when CL was not set'
ERR_MSG_CL_ALPHA_CL_NOT_NUMERIC = 'Failed to calculate confidence level (CL) alpha using CL of'
ERR_MSG_CL_ALPHA_CL_GREATER_THAN_1 = 'Failed to calculate confidence level (CL) alpha. Value was greater than 1'
ERR_MSG_CL_ALPHA_CL_LESS_THAN_0 = 'Failed to calculate confidence level (CL) alpha. Value was less than 0'

ERR_MSG_DEPOSIT_NO_JSON_FILE = 'A JSON file is not avilable for deposit.'
ERR_MSG_DEPOSIT_NO_PDF_FILE = 'A PDF file is not avilable for deposit.'
ERR_MSG_DEPOSIT_NOT_DATAVERSE = 'Deposit functionality is not available for a non-Dataverse file'
ERR_MSG_DEPOSIT_NO_DV_USER = 'The Datavese user could not be for this release.'

ERR_BOOL_TRUE_FALSE_NOT_EQUAL = f'The True and False values cannot be the same'

# Setup Questions

SETUP_Q_01_ATTR = 'radio_depend_on_private_information'
SETUP_Q_01_TEXT = ('Does your data file depend on private information of subjects?',
                   'Question to help determine whether differential privacy is appropriate for this data file.')

SETUP_Q_02_ATTR = 'radio_best_describes'
SETUP_Q_02_TEXT = ('Which of the following best describes your data file?',
                   'The answer is used to set privacy parameters (default epsilon and delta values)'
                   ' which may be changed later in the process.')

SETUP_Q_02_ANSWERS = dict(
    public=('Public Information', None),
    notHarmButConfidential=(('Information that, if disclosed,'
                             ' would not cause material harm,'
                             ' but which the organization has chosen to keep confidential'),
                            {'epsilon': 1, 'delta': 10 - 5}),
    couldCauseHarm=(('Information that could cause risk of material harm to individuals'
                     ' or the organization if disclosed'),
                    {'epsilon': .25, 'delta': 10e-6}),
    wouldLikelyCauseHarm=(('Information that would likely cause serious harm to individuals'
                           ' or the organization if disclosed'),
                          {'epsilon': .05, 'delta': 10e-7}),
    wouldCauseSevereHarm=(('Information that would cause severe harm to individuals or the'
                           ' organization if disclosed. Use of this application is not'
                           ' recommended.'),
                          None),
)
SETUP_Q_02_CHOICES = SETUP_Q_02_ANSWERS.keys()

SETUP_Q_03_ATTR = 'radio_only_one_individual_per_row'
SETUP_Q_03_TEXT = ('Does each individual appear in only one row?',
                   'Used to help determine dataset distance.')


SETUP_Q_04_ATTR = 'secret_sample'
SETUP_Q_04_TEXT = ('Is your data a secret and simple random sample from a larger population?',
                   ('If the data is a simple random sample, we can use methods (amplification)'
                    ' to increase the accuracy and utility of the statistics you create.'))

SETUP_Q_04a_ATTR = 'population_size'  # if SETUP_Q_04_ATTR answer is "yes"
SETUP_Q_04a_TEXT = 'Population size'

SETUP_Q_05_ATTR = 'observations_number_can_be_public'
SETUP_Q_05_TEXT = ('Can the number of observations in your data file be made public knowledge?',
                   ('If the data file size can be made public, we don\'t need to spend a portion'
                    ' of your privacy budget to estimate it.'))

YES_VALUE = 'yes'
NO_VALUE = 'no'
YES_NO_VALUES = [YES_VALUE, NO_VALUE]
YES_NO_QUESTIONS = [SETUP_Q_01_ATTR, SETUP_Q_03_ATTR, SETUP_Q_04_ATTR, SETUP_Q_05_ATTR]

SETUP_QUESTION_LOOKUP = {
    SETUP_Q_01_ATTR: SETUP_Q_01_TEXT,
    SETUP_Q_02_ATTR: SETUP_Q_02_TEXT,
    SETUP_Q_03_ATTR: SETUP_Q_03_TEXT,
    SETUP_Q_04_ATTR: SETUP_Q_04_TEXT,
    SETUP_Q_05_ATTR: SETUP_Q_05_TEXT,
}
SETUP_QUESTION_LIST = [SETUP_Q_01_ATTR,
                       SETUP_Q_02_ATTR,
                       SETUP_Q_03_ATTR,]
                       #SETUP_Q_04_ATTR,
                       #SETUP_Q_05_ATTR]

EPSILON_QUESTION_LIST = [SETUP_Q_04_ATTR,
                         SETUP_Q_04a_ATTR,
                         SETUP_Q_05_ATTR]

ERR_MSG_DATASET_QUESTIONS_NOT_DICT = 'Dataset questions must be a dictionary'
ERR_MSG_DATASET_QUESTIONS_INVALID_KEY= 'Invalid key for dataset questions: "{key}"'
ERR_MSG_DATASET_QUESTIONS_INVALID_VALUE = 'Invalid value ("{value}") for dataset question {"{key}"}'
ERR_MSG_DATASET_YES_NO_QUESTIONS_INVALID_VALUE = ('Dataset question "{key}" should have'
                                                  ' a "yes" or "no" answer, not "{value}"')
ERR_MSG_POPULATION_SIZE_MISSING = ('If this is a sample from a population, the population size'
                                   ' must be an integer. Currently, it is: {pop_size}')
ERR_MSG_POPULATION_CANNOT_BE_NEGATIVE = ('The population must be a positive integer. Currently, it is: {pop_size}')
