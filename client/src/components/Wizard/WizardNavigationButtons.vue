<template>
  <div
      class="wizard-buttons-wrapper sticky-wizard rounded text-center wizard_navigator"
      :class="{
      'py-10': $vuetify.breakpoint.mdAndUp,
      'py-5': $vuetify.breakpoint.smAndDown
    }"
  >
    <div
        class="mt-3"
        :class="{
        'mb-12': $vuetify.breakpoint.mdAndUp,
        'mb-6': $vuetify.breakpoint.smAndDown
      }"
    >
      <v-icon left>mdi-timer</v-icon>
      <small>Remaining: {{ remainingTime }}</small>
    </div>

    <div
        :class="{ 'd-flex justify-space-around': $vuetify.breakpoint.smAndDown }"
    >
      <Button
          :disabled="stepperPosition === 0"
          color="primary"
          outlined
          :click="() => (dialogGoBack = true)"
          classes="mb-2 d-block"
          :class="{
          'mx-auto': $vuetify.breakpoint.mdAndUp
        }"
          label="Back"
      />

      <Button
          color="primary"
          outlined
          :click="handleSave"
          classes="px-0 mb-2 d-block"
          :class="{
          'mx-auto': $vuetify.breakpoint.mdAndUp
        }"
      >Save<small class="font-weight-regular">
        (Last saved at {{ lastSavedAt }})</small
      >
      </Button>

      <Button
          v-if="stepperPosition !== LAST_STEP_INDEX"
          classes="d-block"
          :class="{
          'mx-auto': $vuetify.breakpoint.mdAndUp
        }"
          color="primary"
          :click="handleContinue"
          :disabled="isContinueDisabled"
          label="Continue"
      />

      <Button
          v-else
          color="primary"
          :class="{
          'mx-auto': $vuetify.breakpoint.mdAndUp
        }"
          :click="() => $root.$emit('areStatisticsSubmitted')"
          label="Submit statistics"
      />
    </div>

    <GoBackDialog v-on:confirm="handleBack" :dialog.sync="dialogGoBack"/>
  </div>
</template>

<style lang="scss" scoped>
.sticky-wizard {
  position: sticky;
  top: 116px;
  z-index: 1;
}
</style>

<script>
import Button from "../DesignSystem/Button.vue";
import GoBackDialog from "./GoBackDialog.vue";

export default {
  components: {Button, GoBackDialog},
  name: "WizardNavigationButtons",
  props: ["steps", "stepperPosition"],

  methods: {
    handleContinue: function () {
      window.scrollTo(0, 0);
      this.$emit("update:stepperPosition", this.stepperPosition + 1);
    },
    handleBack: function () {
      this.dialogGoBack = false;
      this.$emit("update:stepperPosition", this.stepperPosition - 1);
    },
    handleSave: function () {
      //TODO: Implement Save handler
      alert("save!");
    }
  },
  data: () => ({
    LAST_STEP_INDEX: 4,
    lastSavedAt: "00:00",
    remainingTime: "2d 14h 36min",
    dialogGoBack: false
  }),
  computed: {
    isContinueDisabled: function () {
      return !this.steps[this.stepperPosition].completed;
    }
  }
};
</script>
