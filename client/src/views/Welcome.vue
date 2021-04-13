<template>
  <div class="welcome mt-16">
    <EventSuccessAlert
        text="Account activated successfully."
        queryParam="accountActivated"
    />
    <v-container>
      <v-row>
        <v-col>
          <h1 class="title-size-1">Welcome, Danny</h1>
          <CreateDPStatistics/>
          <h2 class="title-size-2 font-weight-bold mt-16">My Data</h2>
          <MyDataTable :datasets="variables" :paginationVisible="false"/>
          <v-btn
              color="primary"
              outlined
              class="font-weight-bold mt-5"
              @click="$router.push('/my-data')"
          >
            See all my datasets
          </v-btn>
        </v-col>
      </v-row>
    </v-container>
    <SupportBanner/>
  </div>
</template>

<script>
import EventSuccessAlert from "../components/Home/EventSuccessAlert.vue";
import MyDataTable from "../components/MyData/MyDataTable.vue";
import SupportBanner from "../components/SupportBanner.vue";
import CreateDPStatistics from "../components/Welcome/CreateDPStatistics.vue";

export default {
  name: "Welcome",
  components: {
    CreateDPStatistics,
    MyDataTable,
    SupportBanner,
    EventSuccessAlert
  },
  data: () => ({
    variables: [
      {
        dataset: "California Demographic Dataset",
        status: "in_progress",
        datasetId: "abcd1234"
      },
      {
        dataset: "Tokio Demographic Dataset",
        status: "in_execution",
        datasetId: "abcd1234"
      }
    ]
  })
};
</script>
