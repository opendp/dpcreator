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
                <ConfirmVariables :stepperPosition="stepperPosition" v-on:stepCompleted="updateStepStatus"/>
              </v-stepper-content>
              <v-stepper-content :complete="stepperPosition > 1" step="1">
                <CreateStatistics v-on:addVariable="gotoStep(0)" ref="createStatComponent"
                                  :stepperPosition="stepperPosition.sync"
                                  v-on:stepCompleted="updateStepStatus"/>
              </v-stepper-content>
              <v-stepper-content :complete="stepperPosition > 2" step="2">
                <GenerateDPRelease v-on:addStatistic="gotoStep(1)" v-on:stepCompleted="updateStepStatus"/>
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
import CreateStatistics from "@/views/WizardSteps/CreateStatistics.vue";
import GenerateDPRelease from "@/views/WizardSteps/GenerateDPRelease.vue";

export default {
  name: "AnalystWizard",
  components: {
    ConfirmVariables,
    StepperHeader,
    WizardNavigationButtons,
    CreateStatistics,
    GenerateDPRelease
  },
  watch: {
    stepperPosition: function (val, oldVal) {
      if (val == 1) {
        this.$refs.createStatComponent.initializeForm();
      }
    }
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
        this.stepperPosition = stepInformation[this.analysisPlan.userStep].wizardStepper
        for (let index = 0; index < this.stepperPosition; index++) {
          this.steps[index].completed = true
        }
    },
    gotoStep(step) {
      this.stepperPosition = step
    },

  },
  computed: {
    ...mapState('dataset', ['datasetInfo', 'analysisPlan']),
    ...mapState('auth', ['user']),
  },

  data: () => ({
    workflow: "analyst",
    loading: true,
    stepperPosition: 0,
    variableList: null,
    steps: [
      {
        title: "Confirm Variables",
        completed: true
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
