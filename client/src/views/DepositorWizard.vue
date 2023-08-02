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
                <ConfirmVariables
                    :variable-list="variableList"
                    :stepperPosition="stepperPosition"
                    allow-select-all=true
                    v-on:stepCompleted="updateStepStatus"
                    v-on:updateVariable="updateVariable"
                    v-on:updateAllVariables="updateAllVariables"
                />
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
import dataset from "@/api/dataset";

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
      this.stepperPosition = step
    },
    // If we are on the Confirm Variables step, and the DepositorSetup variables
    // are not set, then run the Profiler, else use the existing variables
    initializeVariableList() {
        if (this.getDepositorSetupInfo.variableInfo === null) {
          dataset.runProfiler(this.datasetInfo.objectId).then((resp) => {
            // when profiler returns, save the variables locally, so they can be passed as a prop to
            // Confirm Variables
            this.variableList = resp.data.data.variables
            // also update the store with the new datasetInfo object (which is populated with variables)
            this.$store.dispatch('dataset/setDatasetInfo', this.datasetInfo.objectId)
          })
        } else {
          this.variableList = this.getDepositorSetupInfo.variableInfo
        }
    },
    updateVariable(elem) {
      // make a deep copy so that the form doesn't share object references with the Vuex data
      const elemCopy = JSON.parse(JSON.stringify(elem))
      this.$store.dispatch('dataset/updateVariableInfo', elemCopy)
    },
    updateAllVariables(varsCopy) {
      this.$store.dispatch('dataset/updateAllVariables', varsCopy)
    },
  },
  computed: {
    ...mapState('dataset', ['datasetInfo', 'analysisPlan']),
    ...mapGetters('dataset', ['getDepositorSetupInfo', 'userStep']),
    ...mapState('auth', ['user']),
  },
  watch: {
    stepperPosition: function (val, oldVal) {
      if (val === 1) {
        this.initializeVariableList()
      }
    }
  },
  data: () => ({
    workflow: "depositor",
    loading: true,
    stepperPosition: 0,
    variableList: null,
    variableItems: [],
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
