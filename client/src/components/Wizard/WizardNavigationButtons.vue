<template>
  <div
      class="wizard-buttons-wrapper sticky-wizard text-center grey lighten-4 py-10"
  >
    <v-btn
        :disabled="stepperPosition === 0 ? true : false"
        color="primary"
        outlined
        @click="handleBack"
        class="mb-5 d-block mx-auto"
    >
      Back
    </v-btn>

    <v-btn
        color="primary"
        outlined
        @click="handleSave"
        class="mb-5 d-block mx-auto"
    >
      Save
    </v-btn>
    <v-btn
        v-if="stepperPosition !== LAST_STEP_INDEX"
        class="d-block mx-auto"
        color="primary"
        @click="handleContinue"
        :disabled="!steps[stepperPosition].completed"
    >
      Continue
    </v-btn>
    <v-btn v-else color="primary" @click="$root.$emit('statisticsSubmitted')">
      Submit statistics
    </v-btn>
  </div>
</template>

<script>
export default {
  name: "WizardNavigationButtons",
  props: ["steps", "stepperPosition"],
  methods: {
    handleContinue: function () {
      window.scrollTo(0, 0);
      this.$emit("update:stepperPosition", this.stepperPosition + 1);
    },
    handleBack: function () {
      this.$emit("update:stepperPosition", this.stepperPosition - 1);
    },
    handleSave: function () {
      alert("save!");
    }
  },
  data: () => ({
    LAST_STEP_INDEX: 4
  })
};
</script>
