<template>
  <v-stepper-header class="grey lighten-4">
    <template v-for="(step, i) in steps">
      <v-stepper-step
          :editable="isEditable(i)"
          :key="i"
          :complete="stepperPosition > i"
          :step="i"
          edit-icon="mdi-check"
      >
        {{ step.title }}
      </v-stepper-step>
      <v-divider
          :key="'step-divider-' + i"
          v-if="i !== steps.length - 1"
      ></v-divider>
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
    }
  }
};
</script>
