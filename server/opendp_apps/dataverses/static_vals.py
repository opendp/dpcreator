
HEADER_KEY_DATAVERSE = 'X-Dataverse-key'

# -----------------------------
# Dataverse Manifest Params
#   - sent over via GET
# -----------------------------
DV_PARAM_FILE_ID = 'fileId'
DV_PARAM_SITE_URL = 'site_url'
DV_PARAM_DATASET_PID = 'datasetPid' # dataset DOI
DV_PARAM_FILE_PID = 'filePid'   # file DOI
DV_API_GENERAL_TOKEN = 'apiGeneralToken'

DV_ALL_PARAMS = [DV_PARAM_FILE_ID, DV_PARAM_SITE_URL, DV_PARAM_DATASET_PID,
                 DV_PARAM_FILE_PID, DV_API_GENERAL_TOKEN]
DV_OPTIONAL_PARAMS = [DV_PARAM_FILE_PID,]


# -----------------------------
# Values used when calling
# the Dataverse API
# -----------------------------
# ref: https://guides.dataverse.org/en/latest/api/native-api.html#schema-org-json-ld
EXPORTER_FORMAT_DDI = 'ddi'
EXPORTER_FORMAT_SCHEMA_ORG = 'schema.org'
EXPORTER_FORMATS = [EXPORTER_FORMAT_DDI, EXPORTER_FORMAT_SCHEMA_ORG]

# -----------------------------
# Keys for accessing data within
# Dataverse API responses
# -----------------------------
DV_KEY_STATUS = 'status'
DV_KEY_MESSAGE = 'message'

STATUS_VAL_OK = 'OK'
STATUS_VAL_ERROR = 'ERROR'

SCHEMA_KEY_CONTENTURL = 'contentUrl'
SCHEMA_KEY_DISTRIBUTION = 'distribution'
SCHEMA_KEY_IDENTIFIER = 'identifier'
SCHEMA_KEY_NAME = 'name'

DV_PERSISTENT_USER_ID = 'persistentUserId'
DV_EMAIL = 'email'
DV_FIRST_NAME = 'firstName'
DV_LAST_NAME = 'lastName'

# ----------------------------------
# Keys for Vue -> Django Server API calls
# ----------------------------------
KEY_DP_USER_ID = 'user_id' # OpenDPUser.object_id
KEY_DV_HANDOFF_ID = 'dataverse_handoff_id'  # DataverseHandoff.object_id

DV_DEPOSIT_TYPE_DP_JSON = 'dpJSON'
DV_DEPOSIT_TYPE_DP_PDF = 'dpPDF'
DV_DEPOSIT_TYPES = [DV_DEPOSIT_TYPE_DP_JSON, DV_DEPOSIT_TYPE_DP_PDF]
DV_DEPOSIT_CHOICES = [(x, x) for x in DV_DEPOSIT_TYPES]

# ----------------------------------
# Error messages
# ----------------------------------
ERR_MSG_DEPOSIT_NO_DV_DATASET_INFO = 'This is not a Dataverse dataset'

ERR_MSG_JSON_DEPOSIT_ALREADY_COMPLETE = 'JSON deposit already complete'
ERR_MSG_PDF_DEPOSIT_ALREADY_COMPLETE = 'PDF deposit already complete'

ERR_MSG_JSON_DEPOSIT_FAILED = 'JSON deposit failed'
ERR_MSG_PDF_DEPOSIT_FAILED = 'PDF deposit failed'