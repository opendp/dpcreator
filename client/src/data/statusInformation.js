export default {
    uploaded: {
        label: "Uploaded",
        color: "blue lighten-3",
        icon: "",
        availableActions: ["viewDetails", "continueWorkflow"]
    },
    in_progress: {
        label: "In Progress",
        color: "blue lighten-3",
        icon: "",
        availableActions: ["viewDetails", "continueWorkflow"]
    },
    in_execution: {
        label: "In Execution",
        color: "grey lighten-3",
        icon: "mdi-progress-clock",
        availableActions: ["viewDetails", "cancelExecution"]
    },
    error: {
        label: "Execution Error",
        color: "red lighten-3",
        icon: "mdi-alert",
        availableActions: ["viewDetails"]
    },
    completed: {
        label: "Release Completed",
        color: "light-green lighten-3",
        icon: "",
        availableActions: ["viewDetails"]
    },
    statuses: {
        UPLOADED: "uploaded",
        IN_PROGRESS: "in_progress",
        IN_EXECUTION: "in_execution",
        ERROR: "error",
        COMPLETED: "completed"
    }
};
