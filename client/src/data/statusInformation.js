export default {
    in_progress: {
        label: "In progress",
        color: "blue lighten-3",
        icon: "",
        availableActions: ["viewDetails", "continueWorkflow"]
    },
    in_execution: {
        label: "In execution",
        color: "grey lighten-3",
        icon: "mdi-progress-clock",
        availableActions: ["viewDetails", "cancelExecution"]
    },
    error: {
        label: "Execution error",
        color: "red lighten-3",
        icon: "mdi-alert",
        availableActions: ["viewDetails"]
    },
    completed: {
        label: "Release completed",
        color: "light-green lighten-3",
        icon: "",
        availableActions: ["viewDetails"]
    }
};
