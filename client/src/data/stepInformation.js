import statusInformation from "@/data/statusInformation";

export const STEP_0100_UPLOADED = 'step_100'
export const STEP_0200_VALIDATED = 'step_200'
export const STEP_0300_PROFILE_PROCESSING = 'step_300'
export const STEP_0400_PROFILING_COMPLETE = 'step_400'
export const STEP_0500_VARIABLE_DEFAULTS_CONFIRMED = 'step_500'
export const STEP_0600_EPSILON_SET = 'step_600'
export const STEP_0700_VARIABLES_CONFIRMED = 'step_700'
export const STEP_0800_STATISTICS_CREATED = 'step_800'
export const STEP_0900_STATISTICS_SUBMITTED = 'step_900'
export const STEP_1000_RELEASE_COMPLETE = 'step_1000'
export const STEP_1100_DV_RELEASE_DEPOSITED = 'step_1100'
export const STEP_1200_PROCESS_COMPLETE = 'step_1200'

// Error statuses should begin with 9
export const STEP_9100_VALIDATION_FAILED = 'step_9100'
export const STEP_9200_DATAVERSE_DOWNLOAD_FAILED = 'step_9200'
export const STEP_9300_PROFILING_FAILED = 'step_9300'
export const STEP_9400_CREATE_RELEASE_FAILED = 'step_9400'
export const STEP_9500_RELEASE_CREATION_FAILED = 'error_9500'
export const STEP_9600_RELEASE_DEPOSIT_FAILED = 'error_9600'

export const depositorSteps = [
    STEP_0100_UPLOADED,
    STEP_0200_VALIDATED,
    STEP_0300_PROFILE_PROCESSING,
    STEP_0400_PROFILING_COMPLETE,
    STEP_0500_VARIABLE_DEFAULTS_CONFIRMED,
    STEP_0600_EPSILON_SET
]

export const analystSteps = [
    STEP_0700_VARIABLES_CONFIRMED,
    STEP_0800_STATISTICS_CREATED,
    STEP_0900_STATISTICS_SUBMITTED,
    STEP_1000_RELEASE_COMPLETE,
    STEP_1100_DV_RELEASE_DEPOSITED,
    STEP_1200_PROCESS_COMPLETE
]

// All userSteps that can occur within the wizard stepper.
// Some steps share a stepper position.
export const wizardUserSteps = [
    STEP_0100_UPLOADED,
    STEP_0200_VALIDATED,
    STEP_0300_PROFILE_PROCESSING,
    STEP_0400_PROFILING_COMPLETE,
    STEP_0500_VARIABLE_DEFAULTS_CONFIRMED,
    STEP_0600_EPSILON_SET,
    STEP_0700_VARIABLES_CONFIRMED,
    STEP_0800_STATISTICS_CREATED,
    STEP_0900_STATISTICS_SUBMITTED
]
// Maps Wizard StepperPosition (the index of this array)
// to the userStep to be assigned when the wizard step is completed.
export const wizardNextSteps = [
    STEP_0400_PROFILING_COMPLETE,  //stepperPos 0
    STEP_0500_VARIABLE_DEFAULTS_CONFIRMED,//stepperPos 1
    STEP_0600_EPSILON_SET, //stepperPos 2
    STEP_0800_STATISTICS_CREATED, //stepperPos 3
    STEP_0900_STATISTICS_SUBMITTED //stepperPos 4
]


export default {
    [STEP_0100_UPLOADED]: {
        workflowStatus: statusInformation.statuses.UPLOADED,
        wizardStepper: 0,
        label: 'Dataset Uploaded'
    },
    [STEP_0200_VALIDATED]: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 1,
        label: 'Dataset Validated'
    },
    [STEP_0300_PROFILE_PROCESSING]: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 1,
        label: 'Profile Processing'
    },
    [STEP_0400_PROFILING_COMPLETE]: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 1,
        label: 'Profiling Complete',
    },
    [STEP_0500_VARIABLE_DEFAULTS_CONFIRMED]: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 2,
        label: 'Variable Defaults Confirmed',
    },
    [STEP_0600_EPSILON_SET]: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 3,
        label: 'Epsilon Set',
    },
    [STEP_0700_VARIABLES_CONFIRMED]: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 3,
        label: 'Variables Confirmed'
    },
    [STEP_0800_STATISTICS_CREATED]: {
        workflowStatus: statusInformation.statuses.IN_PROGRESS,
        wizardStepper: 4,
        label: 'Statistics Created'
    },
    [STEP_0900_STATISTICS_SUBMITTED]: {
        workflowStatus: statusInformation.statuses.IN_EXECUTION,
        label: 'Statistics Submitted'
    },
    [STEP_1000_RELEASE_COMPLETE]: {
        workflowStatus: statusInformation.statuses.IN_EXECUTION,
        label: 'Release Complete'
    },
    [STEP_1100_DV_RELEASE_DEPOSITED]: {
        workflowStatus: statusInformation.statuses.IN_EXECUTION,
        label: 'Dataverse Release Deposited'
    },
    [STEP_1200_PROCESS_COMPLETE]: {
        workflowStatus: statusInformation.statuses.COMPLETED,
        label: 'Process Complete'
    },
    [STEP_9100_VALIDATION_FAILED]: {
        workflowStatus: statusInformation.statuses.ERROR,
        label: 'Validation Failed'
    },
    [STEP_9200_DATAVERSE_DOWNLOAD_FAILED]: {
        workflowStatus: statusInformation.statuses.ERROR,
        label: 'Download Failed'
    },
    [STEP_9300_PROFILING_FAILED]: {
        workflowStatus: statusInformation.statuses.ERROR,
        label: 'Profiling Failed'
    },
    [STEP_9400_CREATE_RELEASE_FAILED]: {
        workflowStatus: statusInformation.statuses.ERROR,
        label: 'Create Release Failed'
    },
    [STEP_9500_RELEASE_CREATION_FAILED]: {
        workflowStatus: statusInformation.statuses.ERROR,
        label: 'Create Release Failed'
    },
    [STEP_9600_RELEASE_DEPOSIT_FAILED]: {
        workflowStatus: statusInformation.statuses.ERROR,
        label: 'Release Deposit Failed'
    }
}
