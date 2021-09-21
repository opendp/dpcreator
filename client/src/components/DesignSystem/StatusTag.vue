<template>
  <v-chip data-test="status tag" :class="statusClasses" label :small="$vuetify.breakpoint.smAndDown">
    {{ statusInformation[status].label }}
  </v-chip>
</template>

<script>
import statusInformation from "../../data/statusInformation";

const {
  IN_PROGRESS,
  IN_EXECUTION,
  ERROR,
  COMPLETED
} = statusInformation.statuses;

export default {
  name: "StatusTag",
  data: () => ({
    statusInformation
  }),
  computed: {
    statusClasses: function () {
      switch (this.status) {
        case IN_PROGRESS:
          return "in_progress_status__bg in_progress_status__color--text";
        case IN_EXECUTION:
          return "in_execution_status__bg in_execution_status__color--text";
        case ERROR:
          return "error_status__bg error_status__color--text";
        case COMPLETED:
          return "completed_status__bg completed_status__color--text";
        default:
          return "";
      }
    }
  },
  props: ["status"]
};
</script>
