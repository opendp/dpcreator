<template>
  <div class="wizard-page">
    <v-container v-if="!loading">
      <v-row>
        <v-col>
          <v-stepper v-model="stepperPosition" id="wizard-content" alt-labels>
            <StepperHeader :steps="steps" :stepperPosition="stepperPosition"/>
            <v-stepper-items>
              <span class="d-block mt-5"
              >Used dataset:
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
              <v-stepper-content :complete="stepperPosition > 2" step="2">
                <SetEpsilonValue :stepperPosition="stepperPosition" v-on:stepCompleted="updateStepStatus"/>
              </v-stepper-content>
              <v-stepper-content :complete="stepperPosition > 3" step="3">
                <CreateStatistics ref="createStatComponent" :stepperPosition="stepperPosition.sync"
                                  v-on:stepCompleted="updateStepStatus"/>
              </v-stepper-content>
              <v-stepper-content :complete="stepperPosition > 4" step="4">
                <GenerateDPRelease v-on:stepCompleted="updateStepStatus"/>
              </v-stepper-content>
            </v-stepper-items>
          </v-stepper>
          <WizardNavigationButtons
              :steps="steps"
              :stepperPosition.sync="stepperPosition"
              class="hidden-md-and-up"
          />
        </v-col>
        <v-col cols="3" lg="2" class="hidden-sm-and-down">
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
import stepInformation, {depositorSteps, STEP_0600_EPSILON_SET} from "@/data/stepInformation";


import {mapState, mapGetters} from "vuex";

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
      this.steps[stepNumber].completed = completedStatus;
    },
    // Set the current Wizard stepper position based on the
    // depositorSetup userStep
    initStepperPosition: function () {
      this.stepperPosition = stepInformation[this.getDepositorSetupInfo.userStep].wizardStepper
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
    ...mapGetters('dataset', ['getDepositorSetupInfo']),
    ...mapState('auth', ['user']),
  },
  watch: {
    stepperPosition: function (val, oldVal) {
      // if the new val is more than one step ahead of the oldVal, that means that val is being initialized because
      // the user has come from the 'Continue Workflow' button on the my data page.  So we don't need to go to the
      // next step.
      if (val - oldVal === 1) {
        const completedStep = stepInformation[this.getDepositorSetupInfo.userStep].nextStep
        const completedStepProp = {userStep: completedStep}
        // Update the user step on the DepositorSetup or the Analysis Plan, depending
        // where we are in the Wizard
        if (depositorSteps.includes(completedStep)) {
          const payload = {objectId: this.getDepositorSetupInfo.objectId, props: completedStepProp}
          this.$store.dispatch('dataset/updateDepositorSetupInfo', payload).then(() => {
            // if the step that has just been completed is  STEP_0600_EPSILON_SET, then update the depositorsetupInfo
            // with epsilon and delta, and create the AnalysisPlan before continuing on to the
            // Create Statistics wizard step
            if (completedStep === STEP_0600_EPSILON_SET) {
              console.log("WIZARD - EPSILON SET")
              this.$store.dispatch('dataset/updateDepositorSetupInfo', payload)
                  .then(() => {
                    console.log("UPDATED STEP, now creating Plan")
                    this.$store.dispatch('dataset/createAnalysisPlan', this.datasetInfo.objectId)
                        .then(() => {
                          'plan created'
                        })
                  })
            }
          })

        } else {
          const payload = {objectId: this.analysisPlan.objectId, props: completedStepProp}
          this.$store.dispatch('dataset/updateAnalysisPlan', payload)
        }

      }
      if (val == 3) {
        console.log("INITIALIZE FORM")
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
        title: "Set Epsilon Value",
        completed: false
      },
      {
        title: "Create Statistics",
        completed: false
      },
      {
        title: "Generate DP",
        completed: true
      }
    ]
  })
};
</script>
