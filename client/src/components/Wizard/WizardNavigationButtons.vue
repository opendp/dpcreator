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
                data-test="wizardCompleteButton"
                v-if="stepperPosition === 1 && workflow==='depositor'"
                classes="d-block"
                :class="{
          'mx-auto': $vuetify.breakpoint.mdAndUp
        }"
                color="primary"
                :click="handleComplete"
                :disabled="isContinueDisabled"
                label="Complete"

        />
      <Button
          v-else-if="stepperPosition === 2 && workflow === 'analyst'"
          color="primary"
          data-test="wizardSubmitStatistics"
          :class="{
          'mx-auto': $vuetify.breakpoint.mdAndUp
        }"
          :click="() => $root.$emit('areStatisticsSubmitted')"
          label="Submit Statistics"
      />
      <Button
          data-test="wizardContinueButton"
          v-else
          classes="d-block"
          :class="{
          'mx-auto': $vuetify.breakpoint.mdAndUp
        }"
          color="primary"
          :click="handleContinue"
          :disabled="isContinueDisabled"
          label="Continue"

      />


      <p></p>
      <Button v-if="stepperPosition > 0"
              data-test="wizardGoBackButton"
              classes="d-block"
              :class="{
          'mx-auto': $vuetify.breakpoint.mdAndUp
        }"
              color="primary"
              :click="handleBack"
              label="Go Back"

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
import NETWORK_CONSTANTS from "../../../src/router/NETWORK_CONSTANTS";
import {mapGetters, mapState} from "vuex";
import {analystWizardNextSteps, wizardNextSteps} from "@/data/stepInformation";

export default {
  components: {Button, GoBackDialog},
  name: "WizardNavigationButtons",
  props: ["steps", "stepperPosition", "workflow"],

  methods: {
    handleContinue: function () {
      window.scrollTo(0, 0);
      this.updateUserStep()
    },
      handleComplete: function () {
          const props = {
              userStep: 'step_500'
          }
          console.log('handle complete, props:' + JSON.stringify(props))
          const payload = {objectId: this.getDepositorSetupInfo.objectId, props: props}
          this.$store.dispatch('dataset/updateDepositorSetupInfo',
              payload)
          this.$router.push(`${NETWORK_CONSTANTS.MY_DATA.PATH}`)

      },
    handleBack: function () {
      this.dialogGoBack = false;
      this.$emit("update:stepperPosition", this.stepperPosition - 1);
    },
      saveUserInput() {


      },

      emitStepEvent() {
      this.$emit("update:stepperPosition", this.stepperPosition + 1)
    },
    updateUserStep() {
      let nextStep = null;
      if (this.workflow === 'depositor') {
         nextStep = wizardNextSteps[this.stepperPosition]
      } else {
        nextStep = analystWizardNextSteps[this.stepperPosition]
      }
      this.$store.dispatch('dataset/updateUserStep', nextStep)
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
    ...mapGetters('dataset', ['getDepositorSetupInfo','getUpdatedTime', 'getTimeRemaining']),



    isContinueDisabled: function () {
        console.log('isContinueDisabled, this.stepperPosistion: '+this.stepperPosition)
        console.log('this.steps: ' + JSON.stringify(this.steps))
        console.log('completed: '+this.steps[this.stepperPosition].completed)
      return !this.steps[this.stepperPosition].completed;
    }
  }
};
</script>
