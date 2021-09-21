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
      const completedStep = stepInformation[this.getDepositorSetupInfo.userStep].nextStep
      const completedStepProp = {userStep: completedStep}
      // Update the user step on the DepositorSetup or the Analysis Plan, depending
      // where we are in the Wizard
      if (depositorSteps.includes(completedStep)) {
        const payload = {objectId: this.getDepositorSetupInfo.objectId, props: completedStepProp}
        this.$store.dispatch('dataset/updateDepositorSetupInfo', payload).then(() => {
          // if the step that has just been completed is  STEP_0600_EPSILON_SET, then
          // create the AnalysisPlan before continuing on to the
          // Create Statistics wizard step
          if (completedStep === STEP_0600_EPSILON_SET) {
            this.$store.dispatch('dataset/createAnalysisPlan', this.datasetInfo.objectId)
                .then(() => this.emitStepEvent())
          } else {
            this.emitStepEvent()
          }
        })

      } else {
        const payload = {objectId: this.analysisPlan.objectId, props: completedStepProp}
        this.$store.dispatch('dataset/updateAnalysisPlan', payload).then(() => this.emitStepEvent())
      }

    },


  },
  data: () => ({
    LAST_STEP_INDEX: 4,
    lastSavedAt: "00:00",
    remainingTime: "2d 14h 36min",
    dialogGoBack: false
  }),

  computed: {
    ...mapState('dataset', ['datasetInfo', 'analysisPlan']),
    ...mapGetters('dataset', ['getDepositorSetupInfo', 'getUpdatedTime', 'getTimeRemaining']),

    isContinueDisabled: function () {
      return !this.steps[this.stepperPosition].completed;
    }
  }
};
</script>
