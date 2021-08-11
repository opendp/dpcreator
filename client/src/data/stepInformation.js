import statusInformation from "@/data/statusInformation";

export const STEP_0100_UPLOADED = 'step_100'
export const STEP_0200_VALIDATED = 'step_200'
export const STEP_0300_PROFILE_PROCESSING = 'step_300'
export const STEP_0400_PROFILING_COMPLETE = 'step_400'
export const STEP_0500_VARIABLE_DEFAULTS_CONFIRMED = 'step_500'
export const STEP_0600_EPSILON_SET = 'step_600'
export const STEP_0700_STATISTICS_CREATED = 'step_700'
export const STEP_0800_STATISTICS_SUBMITTED = 'step_800'
export const STEP_0900_RELEASE_COMPLETE = 'step_900'
export const STEP_1000_DV_RELEASE_DEPOSITED = 'step_1000'
export const STEP_1100_PROCESS_COMPLETE = 'step_1100'

// Error statuses should begin with 9
export const STEP_9100_VALIDATION_FAILED = 'step_9100'
export const STEP_9200_DATAVERSE_DOWNLOAD_FAILED = 'step_9200'
export const STEP_9300_PROFILING_FAILED = 'step_9300'
export const STEP_9400_CREATE_RELEASE_FAILED = 'step_9400'
export const STEP_9500_RELEASE_CREATION_FAILED = 'error_9500'
export const STEP_9600_RELEASE_DEPOSIT_FAILED = 'error_9600'

export default {
    // STEP_0100_UPLOADED
    step_100: {
        workflowStatus: statusInformation.statuses.UPLOADED,
        wizardStepper: 0,
        nextStep: STEP_0200_VALIDATED
    },
    // STEP_0200_VALIDATED
    step_200: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 1,
        nextStep: STEP_0300_PROFILE_PROCESSING
    },
    // STEP_0300_PROFILE_PROCESSING
    step_300: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 1,
        nextStep: STEP_0400_PROFILING_COMPLETE
    },
    // STEP_0400_PROFILING_COMPLETE
    step_400: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 1,
        nextStep: STEP_0500_VARIABLE_DEFAULTS_CONFIRMED
    },
    // STEP_0500_VARIABLE_DEFAULTS_CONFIRMED
    step_500: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 2,
        nextStep: STEP_0600_EPSILON_SET
    },
    // STEP_0600_EPSILON_SET
    step_600: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 3,
        nextStep: STEP_0700_STATISTICS_CREATED

    },
    // STEP_9100_VALIDATION_FAILED
    step_9100: {
        workflowStatus: statusInformation.statuses.ERROR,
    },
    // STEP_9200_DATAVERSE_DOWNLOAD_FAILED
    step_9200: {
        workflowStatus: statusInformation.statuses.ERROR,
    },
    // STEP_9300_PROFILING_FAILED
    step_9300: {
        workflowStatus: statusInformation.statuses.ERROR,
    },
    // STEP_9400_CREATE_RELEASE_FAILED
    step_9400: {
        workflowStatus: statusInformation.statuses.ERROR,
    }
}
