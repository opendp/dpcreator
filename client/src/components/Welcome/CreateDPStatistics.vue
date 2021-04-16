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
      You have been redirected to OpenDP from the Harvard Dataverse to create DP
      statistics for this dataset:
    </p>
    <a href="" class="text-decoration-none font-weight-bold my-6 d-block">
      {{ datasetId }} | {{ datasetName }} | {{ datasetInformation }}
    </a>

    <Button
        color="primary"
        classes="d-block"
        :class="{
        'width100 mx-auto': $vuetify.breakpoint.xsOnly
      }"
        :disabled="$vuetify.breakpoint.xsOnly"
        :click="() => $router.push(NETWORK_CONSTANTS.WIZARD.PATH)"
        label="Start the process"
    />
  </div>
</template>

<script>
import Button from "../DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../../router/NETWORK_CONSTANTS";

export default {
  components: {Button},
  name: "CreateDPStatistics",
  //   TODO: This data should be extracted from the URL or other ways
  data: () => ({
    datasetId: "Dataset ID",
    datasetName: "Dataset Name",
    datasetInformation: "Other relevant information",
    NETWORK_CONSTANTS
  })
};
</script>
