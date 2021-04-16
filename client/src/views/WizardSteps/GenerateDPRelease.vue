<template>
  <div>
    <h1 class="title-size-1">Generate DP Release</h1>
    <p>
      The final step is to submit the statistics and generate the differential
      privacy release. This will finalize the current selections and spend your
      allocated privacy budget on them.
    </p>
    <ColoredBorderAlert type="warning">
      <template v-slot:content>
        This action cannot be undone.
      </template>
    </ColoredBorderAlert>
    <v-form class="my-5" ref="form" @submit.prevent="handleFormSubmit">
      <p class="mb-2">
        <strong>Confirm the email to send notifications to:</strong>
      </p>
      <p>{{ email }}*</p>

      <span class="d-block grey--text text--darken-2 mt-0 font-italic"
      >* If you would like to change your email address, you can edit it in
        your profile area.</span
      >

      <Button
          color="primary"
          type="submit"
          classes="mt-5"
          label="Submit statistics"
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
            <StatusTag :status="IN_EXECUTION"/>
            status, you can check the remaining time to complete in the
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
        setTimeout(() => {
          this.areStatisticsSubmitted = false;
          //TODO: Implement the Handler of the response of the statistics submit
          this.releaseLink = `${NETWORK_CONSTANTS.MY_DATA.PATH}/abcd1234`;
          this.areStatisticsReceived = true;
        }, 3000);
      }
    }
  },
  methods: {
    handleFormSubmit: function () {
      if (this.$refs.form.validate()) {
        this.areStatisticsSubmitted = true;
        //TODO: Implement Submit Statistics handler
      }
    }
  },
  data: () => ({
    areStatisticsSubmitted: false,
    //TODO: Change with the email of the current logged user
    email: "danny-fy@gmail.com",
    areStatisticsReceived: false,
    releaseLink: "",
    NETWORK_CONSTANTS,
    IN_EXECUTION
  })
};
</script>
