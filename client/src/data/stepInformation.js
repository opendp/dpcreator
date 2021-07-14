import statusInformation from "@/data/statusInformation";

export default {
    // STEP_0100_UPLOADED
    step_100: {
        workflowStatus: statusInformation.statuses.UPLOADED,
        wizardStepper: 0
    },
    // STEP_0200_VALIDATED
    step_200: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 1
    },
    // STEP_0300_PROFILE_PROCESSING
    step_300: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 1
    },
    // STEP_0400_PROFILING_COMPLETE
    step_400: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 1
    },
    // STEP_0500_VARIABLE_DEFAULTS_CONFIRMED
    step_500: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 2
    },
    // STEP_0600_EPSILON_SET
    step_600: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 3
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
