<template>
  <div>
    <h1 class="title-size-1">Generate DP Release</h1>
    <p>
      The final step is to submit your statistics to generate a differential privacy release.
      <!-- {{
        $t('generate DP.generate text')
      }} -->
    </p>
  <p>Please review your list of statistics below:</p>


    <div v-if="analysisPlan!==null">
      <v-card
          class="soft_primary mb-5 pt-5 pb-2 rounded-lg shadow-card"
          elevation="4"
          :class="{
      'px-3': $vuetify.breakpoint.xsOnly,
      'px-7': $vuetify.breakpoint.smAndUp
    }"
          outlined>
        <v-card-title><b>DP Statistics</b></v-card-title>
        <v-list-item
            v-for="(item, index) in analysisPlan.dpStatistics"
        >
          <v-list-item-content>
            <v-list-item-title>{{ index + 1 }}. <b>{{ item.variable }}</b> - <b>DP {{ item.statistic }}</b>
            </v-list-item-title>
            <v-list-item-subtitle>Epsilon: {{ Number(item.epsilon).toFixed(3) }}, Delta: {{ item.delta }}, Error:
              {{ Number(item.accuracy.value).toPrecision(3) }}, Fixed Value: {{ item.fixedValue }}
            </v-list-item-subtitle>

          </v-list-item-content>
        </v-list-item>

        <v-card-text>
          <p style="color:#000000">If you would like to change this list,
          <a data-test="createStatisticsLink" v-on:click="returnToCreateStatisticsStep">please edit the statistics</a>.
          </p>
        </v-card-text>
      </v-card>
    </div>
    <p></p>

    <v-form class="my-5" ref="form" v-on:submit.prevent="onSubmit">
      <p class="mb-2">
        <strong>Confirm your email to send notifications to:</strong>
      </p>
      <p>{{ user.email }}*</p>

      <span class="d-block grey--text text--darken-2 mt-0 font-italic"
      >* If you would like to change your email address, you can edit it in
        your profile area.</span
      >
    </v-form>

    <ColoredBorderAlert type="warning">
      <template v-slot:content>
        Note: Once you submit the statistics, the action cannot be undone.
        <p>(If needed,
        <a data-test="createStatisticsLink" v-on:click="returnToCreateStatisticsStep">go back and edit your statistics.</a>)</p>
      </template>
    </ColoredBorderAlert>

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
          <h2 v-if="areStatisticsGenerated" class="title-size-2 mb-5">DP Release Complete</h2>
          <h2 v-else class="title-size-2 mb-5">Statistics are being processed</h2>
        </v-card-title>
        <v-card-text class="text--primary">
          <p v-if="areStatisticsGenerated">
            (An email has also been sent with a link to the release.)
          </p>
          <p v-else>
            You will receive an email <strong>when the release is ready </strong>.
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
    /**
     * Return to the "Create Statistics" page
     */
    returnToCreateStatisticsStep() {
      this.$emit("addStatistic");
    },
    /**
     * Handle the form submission
    */
    handleFormSubmit: function () {
      if (this.$refs.form.validate()) {
        this.areStatisticsSubmitted = true;
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