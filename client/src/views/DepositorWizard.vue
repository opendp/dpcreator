<template>
  <div class="wizard-page">
    <v-container v-if="!loading && datasetInfo">
      <v-row>
        <v-col>
          <v-stepper vertical v-model="stepperPosition" id="wizard-content" alt-labels>
            <StepperHeader :steps="steps" :stepperPosition="stepperPosition"/>
            <v-stepper-items>
              <span class="d-block mt-5"
              >Used data file:
                <a href="http://" class="text-decoration-none"
                >{{ datasetInfo.name }}
                  <v-icon small color="primary">mdi-open-in-new</v-icon></a
                ></span
              >
              <v-stepper-content :complete="stepperPosition > 0" step="0">
                <ValidateDataset v-on:stepCompleted="updateStepStatus"/>
              </v-stepper-content>
              <v-stepper-content :complete="stepperPosition > 1" step="1">
                <ConfirmVariables :stepperPosition="stepperPosition" v-on:stepCompleted="updateStepStatus"/>
              </v-stepper-content>
            </v-stepper-items>
          </v-stepper>
          <WizardNavigationButtons
              :steps="steps"
              :workflow="workflow"
              :stepperPosition.sync="stepperPosition"
          />
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style scoped lang="scss">
.v-stepper {
  box-shadow: none;
}

.v-stepper__content {
  padding-left: 0;
}
</style>

<style lang="scss">
.v-stepper__wrapper {
  padding: 1px;
}
</style>

<script>
import ConfirmVariables from "@/views/WizardSteps/ConfirmVariables";
import StepperHeader from "../components/Wizard/StepperHeader.vue";
import WizardNavigationButtons from "../components/Wizard/WizardNavigationButtons.vue";
import ValidateDataset from "./WizardSteps/ValidateDataset.vue";
import stepInformation from "@/data/stepInformation";


import {mapGetters, mapState} from "vuex";
import NETWORK_CONSTANTS from "@/router/NETWORK_CONSTANTS";

export default {
  name: "DepositorWizard",
  components: {
    ConfirmVariables,
    StepperHeader,
    WizardNavigationButtons,
    ValidateDataset
  },
  created() {
          this.initStepperPosition()
          this.loading = false


  },
  methods: {

    updateStepStatus: function (stepNumber, completedStatus) {
      console.log("updateStepStatus: stepNumber: " + stepNumber + " completedStatus: " + completedStatus)
      this.steps[stepNumber].completed = completedStatus;

    },
    // Set the current Wizard stepper position based on the
    // depositorSetup userStep
    initStepperPosition: function () {
      console.log('INIT stepper position')
      if (this.datasetInfo && this.getDepositorSetupInfo) {
        this.stepperPosition = stepInformation[this.userStep].wizardStepper
        for (let index = 0; index < this.stepperPosition; index++) {
          this.steps[index].completed = true
        }
      }
    },
    gotoStep(step) {
      console.log("handling variable event")
      this.stepperPosition = step
    },
    // If we are on the Confirm Variables step, and the DepositorSetup variables
    // are not set, then run the Profiler
    checkProfileData(step) {
      if (step === 1 && this.getDepositorSetupInfo.variableInfo === null) {
        const payload = {userId: this.user.objectId}
        this.$store.dispatch('dataset/runProfiler', payload)
      }

    }
  },
  computed: {
    ...mapState('dataset', ['datasetInfo', 'analysisPlan']),
    ...mapGetters('dataset', ['getDepositorSetupInfo', 'userStep']),
    ...mapState('auth', ['user']),
  },
  watch: {
    stepperPosition: function (val, oldVal) {

      this.checkProfileData(val)
    }
  },
  data: () => ({
    workflow: "depositor",
    loading: true,
    stepperPosition: 0,
    variableList: null,
    steps: [
      {
        title: "Validate Dataset",
        completed: false
      },
      {
        title: "Confirm Variables",
        completed: false
      },
      ]
  })
};
</script>
