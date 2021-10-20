# ---------------------------------
# Confidence level static values
# ---------------------------------
CL_90 = 0.90    # just to look at
CL_95 = 0.95
CL_99 = 0.99

CL_90test_30_bad_confidence_levels = 1 - CL_90
CL_95_ALPHA = 1 - CL_95
CL_99_ALPHA = 1 - CL_99

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
DP_QUANTILE = 'quantile'
DP_STATS_CHOICES = [DP_MEAN, DP_SUM, DP_COUNT, DP_HISTOGRAM, DP_QUANTILE]

# --------------------------------------
# Missing value handling
# --------------------------------------
MISSING_VAL_DROP = 'drop'
MISSING_VAL_INSERT_RANDOM = 'insert_random'
MISSING_VAL_INSERT_FIXED = 'insert_fixed'
MISSING_VAL_HANDLING_TYPES = [MISSING_VAL_DROP, MISSING_VAL_INSERT_RANDOM, MISSING_VAL_INSERT_FIXED]

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