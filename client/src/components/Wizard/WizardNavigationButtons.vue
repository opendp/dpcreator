<template>

  <div
      class="wizard-buttons-wrapper sticky-wizard rounded text-center wizard_navigator"
      :class="{
      'py-10': $vuetify.breakpoint.mdAndUp,
      'py-5': $vuetify.breakpoint.smAndDown
    }"
  >


    <div
        :class="{ 'd-flex justify-space-around': $vuetify.breakpoint.smAndDown }"
    >



      <Button
          data-test="wizardContinueButton"
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
    <div
        class="mt-3"
        :class="{
        'mb-12': $vuetify.breakpoint.mdAndUp,
        'mb-6': $vuetify.breakpoint.smAndDown
      }"
    >


    </div>
    <small class="font-weight-regular">
      Last saved: {{ getUpdatedTime }}</small
    ><br></br>
    <v-icon left>mdi-timer</v-icon>
    <small>Remaining: {{ getTimeRemaining }}</small>
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
import {mapState, mapGetters} from "vuex";
import stepInformation, {depositorSteps, STEP_0600_EPSILON_SET} from "@/data/stepInformation";

export default {
  components: {Button, GoBackDialog},
  name: "WizardNavigationButtons",
  props: ["steps", "stepperPosition"],

  methods: {
    handleContinue: function () {
      window.scrollTo(0, 0);
      this.updateUserStep()
    },
    handleBack: function () {
      this.dialogGoBack = false;
      this.$emit("update:stepperPosition", this.stepperPosition - 1);
    },
    emitStepEvent() {
      this.$emit("update:stepperPosition", this.stepperPosition + 1)
    },
    updateUserStep() {
      this.$store.dispatch('dataset/updateUserStep', this.stepperPosition)
      this.emitStepEvent()


    },


  },
  data: () => ({
    LAST_STEP_INDEX: 4,
    lastSavedAt: "",
    remainingTime: "",
    dialogGoBack: false
  }),

  computed: {
    ...mapGetters('dataset', ['getUpdatedTime', 'getTimeRemaining']),

    isContinueDisabled: function () {
      return !this.steps[this.stepperPosition].completed;
    }
  }
};
</script>
