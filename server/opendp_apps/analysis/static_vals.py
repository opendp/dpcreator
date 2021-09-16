
CI_95 = 0.05
CI_99 = 0.01
CI_CHOICES = (
    (CI_95, '95% CI'),
    (CI_99, '99% CI'),
)

# --------------------------------------
# Statistic Types
# --------------------------------------
DP_MEAN = 'mean'
DP_SUM = 'sum'
DP_COUNT = 'count'
DP_HISTOGRAM = 'histogram'
DP_QUANTILE = 'quantile'
DP_STATS_CHOICES = [DP_MEAN, DP_SUM, DP_COUNT, DP_HISTOGRAM, DP_QUANTILE]

DP_STAT_NEED_MIN_MAX = {DP_MEAN: True,
                        DP_HISTOGRAM: False}


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
ERR_MSG_DATASET_ID_REQUIRED = 'The DataSetInfo id is required.'
ERR_MSG_ANALYSIS_ID_REQUIRED = 'The AnalysisPlan id is required.'


ERR_MSG_USER_REQUIRED = 'The OpenDP user is required.'
ERR_MSG_NO_DATASET = 'DataSetInfo object not found for this object_id and creator'
ERR_MSG_SETUP_INCOMPLETE = 'Depositor setup is not complete'

ERR_MSG_NO_ANALYSIS_PLAN = 'AnalysisPlan object not found for this object_id and creator'
ERR_MSG_FIELDS_NOT_UPDATEABLE = 'These fields are not updatable'

ERR_MSG_BAD_TOTAL_EPSILON = 'The depositor setup info has an invalid epsilon value'
ERR_MSG_INVALID_MIN_MAX = 'The "max" must be greater than the "min"'

ERR_IMPUTE_PHRASE_MIN = 'cannot be less than the "min"'
ERR_IMPUTE_PHRASE_MAX = 'cannot be more than the "max"'