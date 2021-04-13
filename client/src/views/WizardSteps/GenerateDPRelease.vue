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
      <v-text-field
          class="top-borders-radius width50"
          :value="email + '*'"
          readonly
          type="email"
          hide-details
          background-color="blue lighten-4"
      ></v-text-field>
      <span class="d-block grey--text text--darken-2 mt-0"
      >*If you would like to change your email address, you can edit it in
        your profile area</span
      >

      <v-btn color="primary" type="submit" class="mt-5"
      >Submit statistics
      </v-btn>
    </v-form>
    <v-overlay :value="statisticsSubmitted">
      <div class="d-flex flex-column align-center">
        <v-progress-circular indeterminate size="64"></v-progress-circular>
        <p class="mt-10 title-size-2">Uploading statistics</p>
      </div>
    </v-overlay>
    <v-dialog
        v-model="statisticsReceived"
        width="60%"
        @click:outside="$router.push('/')"
    >
      <v-card elevation="2" class="px-10 py-12">
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
            <v-chip color="grey lighten-3" label>
              <v-icon left small>
                mdi-progress-clock
              </v-icon>
              In execution
            </v-chip>
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
          <v-btn
              color="primary"
              class="mr-2 px-5"
              @click="$router.push(releaseLink)"
          >
            View Data Details
          </v-btn>
          <v-btn
              color="primary"
              outlined
              class="px-5"
              @click="$router.push('/')"
          >
            Go to Home
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import ColoredBorderAlert from "../../components/DynamicHelpResources/ColoredBorderAlert.vue";

export default {
  name: "GenerateDPRelease",
  components: {ColoredBorderAlert},
  mounted() {
    const that = this;
    this.$root.$on("statisticsSubmitted", function () {
      that.statisticsSubmitted = true;
    });
  },
  watch: {
    statisticsSubmitted: function (newStatisticsSubmitted) {
      const that = this;
      if (newStatisticsSubmitted === true) {
        setTimeout(function () {
          that.statisticsSubmitted = false;
          that.releaseLink = "/my-data/abcd1234";
          that.statisticsReceived = true;
        }, 3000);
      }
    }
  },
  methods: {
    handleFormSubmit: function () {
      if (this.$refs.form.validate()) {
        this.statisticsSubmitted = true;
      }
    }
  },
  data: () => ({
    statisticsSubmitted: false,
    email: "danny-fysdfsdfsfsdfsdfsdfdsf@gmail.com",
    statisticsReceived: false,
    releaseLink: ""
  })
};
</script>
