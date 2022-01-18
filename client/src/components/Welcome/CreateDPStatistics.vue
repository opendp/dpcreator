<template>
  <div
      class="soft_primary rounded-lg mt-10"
      :class="{
      'py-16 px-4': $vuetify.breakpoint.xsOnly,
      'pa-16': $vuetify.breakpoint.smAndUp
    }"
  >
    <h2 class="title-size-2 mb-6 font-weight-bold">Create DP Statistics</h2>
    <p>
      You have been redirected to DP Creator from the <b>{{ datasetInfo.installationName }}</b> to create DP
      statistics for this data file:
    </p>
    <a v-bind:class="beginWizard" @click="beginWizard" class="text-decoration-none font-weight-bold my-6 d-block">{{ datasetInfo.datasetDoi }}
      | {{ datasetInfo.datasetSchemaInfo.name }}
      | {{ datasetInfo.fileSchemaInfo.name }}
    </a>

    <div v-if="showButton">
      <Button
          data-test="Start Process"
          color="primary"
          classes="d-block"
          :class="{
        'width100 mx-auto': $vuetify.breakpoint.xsOnly
      }"
          :disabled="$vuetify.breakpoint.xsOnly"
          :click="() => beginWizard()"
          label="Continue"
      />
    </div>
  </div>
</template>

<script>
import Button from "../DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../../router/NETWORK_CONSTANTS";
import stepInformation, {STEP_0100_UPLOADED} from "@/data/stepInformation";

export default {
  components: {Button},
  name: "CreateDPStatistics",
  props: ["datasetInfo"],


  data: () => ({
    NETWORK_CONSTANTS

  }),
  computed: {
    showButton() {
      return this.datasetInfo.depositorSetupInfo.userStep === STEP_0100_UPLOADED
    },
  },
  methods: {

    beginWizard() {
      this.$store.dispatch('dataset/setDatasetInfo', this.datasetInfo.objectId)
          .then(() => {
            this.$router.push(`${NETWORK_CONSTANTS.WIZARD.PATH}`)

          })
    }
  }
};
</script>
