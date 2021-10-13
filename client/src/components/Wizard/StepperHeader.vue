<template>
  <v-stepper-header class="wizard_navigator rounded">
    <template v-for="(step, i) in steps">
      <v-stepper-step
          :editable="isEditable(i)"
          :data-test="'step' + i"
          :key="i + '-v1'"
          :complete="isStepCompleted(i)"
          :step="i"
          edit-icon="mdi-check"
      >
        {{ step.title }}
      </v-stepper-step>
      <v-divider :key="i + '-v2'" v-if="i !== steps.length - 1"></v-divider>
    </template>
  </v-stepper-header>
</template>

<style lang="scss" scoped>
.v-stepper__header {
  box-shadow: unset;
}

.v-stepper__step {
  padding: 20px;
}

.v-stepper__step--active {
  font-weight: bold;
}

.v-stepper__step--editable:hover {
  background: transparent !important;
}
</style>

<style lang="scss">
.v-application .v-stepper__label {
  @media screen and (max-width: 1080px) {
    font-size: 0.75rem;
  }
}
</style>

<script>
export default {
  name: "StepperHeader",
  props: ["steps", "stepperPosition"],
  methods: {
    isEditable(step) {
      let editable = true;
      if (step !== 0) {
        for (let i = step; i >= 1; i--) {
          editable = editable && this.steps[i - 1].completed;
        }
      }
      return editable;
    },
    isStepCompleted(i) {
      return this.stepperPosition > i;
    }
  }
};
</script>
