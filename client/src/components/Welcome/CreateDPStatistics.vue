<template>
  <div class="blue lighten-4 rounded-lg pa-16 mt-10">
    <h2 class="title-size-2 mb-6 font-weight-bold">Create DP Statistics</h2>
    <p>
      You have been redirected to OpenDP from the Harvard Dataverse to create DP
      statistics for this dataset:
    </p>
    <a href="" class="text-decoration-none font-weight-bold my-6 d-block">
      {{ datasetId }} | {{ datasetName }} | {{ datasetInformation }}
    </a>
    <v-btn color="primary" class="d-block" @click="$router.push('/wizard')"
    >Start the process
    </v-btn
    >
  </div>
</template>

<script>
export default {
  name: "CreateDPStatistics",
  data: () => ({
    datasetId: "Dataset ID",
    datasetName: "Dataset Name",
    datasetInformation: "Other relevant information"
  })
};
</script>
