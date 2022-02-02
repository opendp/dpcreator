<template>
  <div>
    <h1 class="title-size-1">Generate DP Release</h1>
    <p>
      {{
        $t('generate DP.generate text')
      }}
    </p>
    <ColoredBorderAlert type="warning">
      <template v-slot:content>
        This action cannot be undone.
      </template>
    </ColoredBorderAlert>
    <span> (Need to add or edit the statistics?
            <a data-test="addStatisticsLink" v-on:click="addStatistic">Go back to the Create Statistics step. </a>
            ) </span>
    <v-form class="my-5" ref="form" @submit.prevent="handleFormSubmit">
      <p class="mb-2">
        <strong>Confirm the email to send notifications to:</strong>
      </p>
      <p>{{ user.email }}*</p>

      <span class="d-block grey--text text--darken-2 mt-0 font-italic"
      >* If you would like to change your email address, you can edit it in
        your profile area.</span
      >

      <Button
          color="primary"
          type="submit"
          classes="mt-5"
          label="Submit Statistics"
          data-test="Submit statistics"
      />
    </v-form>
    <v-overlay :value="areStatisticsSubmitted">
      <div class="d-flex flex-column align-center">
        <v-progress-circular indeterminate size="64"></v-progress-circular>
        <p class="mt-10 title-size-2">Uploading statistics</p>
      </div>
    </v-overlay>
    <v-dialog
        v-model="areStatisticsReceived"
        :width="$vuetify.breakpoint.smAndDown ? '90%' : '45%'"
        @click:outside="$router.push(NETWORK_CONSTANTS.HOME.PATH)"
    >
      <v-card elevation="2" class="px-10 py-12">
        <v-icon
            style="position: absolute; right: 40px"
            @click="() => $router.push(NETWORK_CONSTANTS.HOME.PATH)"
        >mdi-close
        </v-icon
        >
        <v-card-title>
          <h2 class="title-size-2 mb-5">Statistics are being processed</h2>
        </v-card-title>
        <v-card-text class="text--primary">
          <p>
            <strong>You will receive an email </strong>to confirm the submission
            and another one <strong>when the release is ready </strong>
          </p>
          <p>
            Your statistics are now on
            <StatusTag data-test="generate release status" :status="status"/>
            status, you can view more details in the
            <router-link
                :to="releaseLink"
                class="font-weight-bold text-decoration-none"
            >Data details
              <v-icon small color="primary"
              >mdi-open-in-new
              </v-icon
              >
            </router-link
            >
            page.
          </p>
        </v-card-text>
        <v-card-actions>
          <Button
              color="primary"
              classes="mr-2 px-5"
              :click="() => $router.push(releaseLink)"
              label="View Data Details"
              data-test="View Data Details"
          />
          <Button
              color="primary"
              outlined
              classes="px-5"
              :click="() => $router.push(NETWORK_CONSTANTS.HOME.PATH)"
              label="Go to Home"
          />
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import Button from "../../components/DesignSystem/Button.vue";
import ColoredBorderAlert from "../../components/DynamicHelpResources/ColoredBorderAlert.vue";
import NETWORK_CONSTANTS from "../../router/NETWORK_CONSTANTS";
import statusInformation from "../../data/statusInformation";
import StatusTag from "../../components/DesignSystem/StatusTag.vue";
import {mapState, mapGetters} from "vuex";
import stepInformation, {STEP_0900_STATISTICS_SUBMITTED} from "@/data/stepInformation";


const {IN_EXECUTION} = statusInformation.statuses;

export default {
  name: "GenerateDPRelease",
  components: {ColoredBorderAlert, Button, StatusTag},
  mounted() {
    this.$root.$on("areStatisticsSubmitted", () => {
      this.areStatisticsSubmitted = true;
    });
  },
  watch: {
    areStatisticsSubmitted: function (newareStatisticsSubmitted) {
      if (newareStatisticsSubmitted === true) {
        this.areStatisticsReceived = true;
        this.$store.dispatch('dataset/generateRelease', this.analysisPlan.objectId).then((resp) => {
          console.log("store generateRelease(), resp: " + resp)
          this.areStatisticsGenerated = true
        })
      }
    }
  },
  methods: {
    addStatistic() {
      this.$emit("addStatistic")
    },
    handleFormSubmit: function () {
      if (this.$refs.form.validate()) {
        this.areStatisticsSubmitted = true;
        //TODO: make call to Release API to submit statistics
        const completedStepProp = {
          userStep: STEP_0900_STATISTICS_SUBMITTED
        }
        const payload = {objectId: this.analysisPlan.objectId, props: completedStepProp}
        this.$store.dispatch('dataset/updateAnalysisPlan', payload)


      }
    }
  },
  data: () => ({
    areStatisticsSubmitted: false,
    areStatisticsReceived: false,
    areStatisticsGenerated: false,

    NETWORK_CONSTANTS,
    IN_EXECUTION
  }),
  computed: {
    ...mapState('auth', ['user']),
    ...mapState('dataset', ['analysisPlan']),
    ...mapGetters('dataset', ['userStep']),
    status: function () {
      return stepInformation[this.userStep].workflowStatus
    },
    releaseLink: function () {
      return `${NETWORK_CONSTANTS.MY_DATA_DETAILS.PATH}`

    }
  }
};
</script>
