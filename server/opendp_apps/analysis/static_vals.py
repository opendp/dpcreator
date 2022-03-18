
NOISE_GEOMETRIC_MECHANISM = 'Geometric'
NOISE_LAPLACE_MECHANISM = 'Laplace'


"""
Epsilon related values
As a rule of thumb, Epsilon should be thought of as a small number, between approximately 1/1000
and 1.

When checking max_epsilon, offset it by 10**-14 to avoid
  floating point addition issues. e.g. exceeding an espilon of 1 by: 0.0000000000000001
"""
MAX_EPSILON_OFFSET = 10**-14

# ---------------------------------
# Confidence level static values
# ---------------------------------
CL_90 = 0.90    # just to look at
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
DP_STATS_CHOICES = [DP_MEAN,
                    DP_SUM,
                    DP_COUNT,
                    DP_HISTOGRAM,
                    # DP_HISTOGRAM_CATEGORICAL,
                    # DP_HISTOGRAM_INTEGER,
                    DP_QUANTILE,
                    DP_VARIANCE]

# --------------------------------------
# Missing value handling
# --------------------------------------
MISSING_VAL_DROP = 'drop'
MISSING_VAL_INSERT_RANDOM = 'insert_random'
MISSING_VAL_INSERT_FIXED = 'insert_fixed'
MISSING_VAL_HANDLING_TYPES = [MISSING_VAL_DROP, MISSING_VAL_INSERT_RANDOM, MISSING_VAL_INSERT_FIXED]
MISSING_VAL_HANDING_LABELS = {
    MISSING_VAL_DROP: "Drop Missing Value",
    MISSING_VAL_INSERT_RANDOM: "Insert Random Value",
    MISSING_VAL_INSERT_FIXED: "Insert Fixed Value",
}
def missing_val_label(missing_val_type):
    assert missing_val_type in MISSING_VAL_HANDING_LABELS,\
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

ERR_MSG_CL_ALPHA_CL_NOT_SET = 'Attempted to calculate confidence level (CL) alpha when CL was not set'
ERR_MSG_CL_ALPHA_CL_NOT_NUMERIC = 'Failed to calculate confidence level (CL) alpha using CL of'
ERR_MSG_CL_ALPHA_CL_GREATER_THAN_1 = 'Failed to calculate confidence level (CL) alpha. Value was greater than 1'
ERR_MSG_CL_ALPHA_CL_LESS_THAN_0 = 'Failed to calculate confidence level (CL) alpha. Value was less than 0'

ERR_MSG_DEPOSIT_NO_JSON_FILE = 'A JSON file is not avilable for deposit.'
ERR_MSG_DEPOSIT_NO_PDF_FILE = 'A PDF file is not avilable for deposit.'
ERR_MSG_DEPOSIT_NOT_DATAVERSE = 'Deposit functionality is not available for a non-Dataverse file'
ERR_MSG_DEPOSIT_NO_DV_USER = 'The Datavese user could not be for this release.'