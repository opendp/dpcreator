<template>
  <div class="wizard-page">
    <v-container v-if="!loading && datasetInfo">
      <v-row>
        <v-col>
          <v-stepper v-model="stepperPosition" id="wizard-content" alt-labels>
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
import SetEpsilonValue from "./WizardSteps/SetEpsilonValue.vue";
import CreateStatistics from "./WizardSteps/CreateStatistics.vue";
import GenerateDPRelease from "./WizardSteps/GenerateDPRelease.vue";
import StepperHeader from "../components/Wizard/StepperHeader.vue";
import WizardNavigationButtons from "../components/Wizard/WizardNavigationButtons.vue";
import ValidateDataset from "./WizardSteps/ValidateDataset.vue";
import stepInformation from "@/data/stepInformation";


import {mapGetters, mapState} from "vuex";

export default {
  name: "Wizard",
  components: {
    ConfirmVariables,
    SetEpsilonValue,
    CreateStatistics,
    GenerateDPRelease,
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
      if (val == 3) {
        this.$refs.createStatComponent.initializeForm();
      }
      this.checkProfileData(val)
    }
  },
  data: () => ({
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
      {
        title: "Sampling Frame",
        completed: false
      },
      {
        title: "Create Statistics",
        completed: false
      },
      {
        title: "Generate DP Release",
        completed: true
      }
    ]
  })
};
</script>
