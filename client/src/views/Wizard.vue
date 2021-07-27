<template>
  <div class="wizard-page">
    <v-container v-if="!loading">
      <v-row>
        <v-col>
          <v-stepper v-on:change="alertChange" v-model="stepperPosition" id="wizard-content" alt-labels>
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
                <SetEpsilonValue v-on:stepCompleted="updateStepStatus"/>
              </v-stepper-content>
              <v-stepper-content :complete="stepperPosition > 3" step="3">
                <CreateStatistics v-on:stepCompleted="updateStepStatus"/>
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
import stepInformation from "@/data/stepInformation";
import dataset from "@/api/dataset";

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
    const objectId = this.$route.params.id
    this.$store.dispatch('dataset/setDatasetInfo', objectId)
        .then(() => {
          this.initStepperPosition()
          this.loading = false

        })

  },
  methods: {
    alertChange(step) {
      console.log("change!" + step)
      if (step === 1) {
        this.runProfiler()
      }
    },
    updateStepStatus: function (stepNumber, completedStatus) {
      console.log('update step!')
      this.steps[stepNumber].completed = completedStatus;
    },
    // Set the current Wizard stepper position based on the
    // depositorSetup userStep
    initStepperPosition: function () {
      this.stepperPosition = stepInformation[this.getDepositorSetupInfo.userStep].wizardStepper
    },
    runProfiler() {
      dataset.startProfiler(this.datasetInfo.objectId).then(() => console.log('posted to profiler'))

      const prefix = 'ws://'
      const websocketId = 'ws_' + this.user.objectId
      console.log("running profiler, before chatsocket")
      const chatSocket = new WebSocket(
          prefix + window.location.host + '/async_messages/ws/profile/' + websocketId + '/'
      );

      /* ---------------------------------------------- */
      /* Add a handler for incoming websocket messages  */
      /* ---------------------------------------------- */
      chatSocket.onmessage = function (e) {

        // parse the incoming JSON to a .js object
        const ws_data = JSON.parse(e.data);

        /* "ws_msg" attributes are the defined in the Python WebsocketMessage object
             msg_type (str): expected "PROFILER_MESSAGE"
             success (boolean):  error detected?
             user_message (str): description of what happened
             msg_cnt (int): Not used for the profiler
             data: Profile data, if it exists, JSON
             timestamp: timestamp

            - reference: opendp_apps/async_messages/websocket_message.py
        */
        const ws_msg = ws_data.message

        // "ws_msg.msg_type": should be 'PROFILER_MESSAGE'
        if (ws_msg.msg_type !== 'PROFILER_MESSAGE') {

          console.log('unknown msg_type: ' + ws_msg.msg_type);
        } else {

          // ---------------------------------------
          // "ws_msg.success": Did it work?
          // ---------------------------------------
          if (ws_msg.success === true) {
            console.log('-- success message');
          } else if (ws_msg.success === false) {
            console.log('-- error message');
            alert(ws_msg.user_message);
          } else {
            console.log('-- error occurred!')
            return;
          }
          console.log('ws_msg.user_message: ' + ws_msg.user_message);


          if (ws_msg.data) {
            //console.log(typeof 42);

            const profileStr = JSON.stringify(JSON.parse(ws_msg.data.profile_str), null, 2);
            console.log(typeof ws_msg.data);
            console.log('>>DATA<< ws_msg.data: ' + profileStr);


          }

        }

        chatSocket.onclose = function (e) {
          console.error('Chat socket closed unexpectedly');
        };
        chatSocket.onerror = function (e) {
          console.error('onerror: ' + e);
        };
      };

    }
  },
  computed: {
    ...mapState('dataset', ['datasetInfo']),
    ...mapGetters('dataset', ['getDepositorSetupInfo']),
    ...mapState('auth', ['user']),
  },
  data: () => ({
    loading: true,
    stepperPosition: 0,
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
