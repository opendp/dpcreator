<template>
  <div class="my-data mt-16">
    <v-container>
      <v-sheet rounded="lg">
        <v-container>
          <h1 class="title-size-1">My Data</h1>
          <v-row>
            <v-col cols="7">
              <p>
                Check your differential privacy releases and pending processes.
                Click on View details to know more about them and their
                statuses.
              </p>
            </v-col>
            <v-col offset-md="1">
              <v-text-field
                  v-model="search"
                  label="Search Dataset"
                  outlined
                  dense
                  append-icon="mdi-magnify"
              ></v-text-field>
            </v-col>
          </v-row>
          <MyDataTable
              :datasets="variables"
              :searchTerm="search"
              :itemsPerPage="5"
          />
        </v-container>
      </v-sheet>
    </v-container>
  </div>
</template>

<script>
import MyDataTable from "../components/MyData/MyDataTable.vue";

export default {
  name: "MyData",
  components: {MyDataTable},

  data: () => ({
    search: "",
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
      },
      {
        dataset: "USA Demographic Dataset",
        status: "error",
        datasetId: "abcd1234"
      },
      {
        dataset: "Example Demographic Dataset",
        status: "completed",
        datasetId: "abcd1234"
      },
      {
        dataset: "Tokio Demographic Dataset",
        status: "in_execution",
        datasetId: "abcd1234"
      },
      {
        dataset: "USA Demographic Dataset",
        status: "error",
        datasetId: "abcd1234"
      },
      {
        dataset: "Tokio Demographic Dataset",
        status: "in_execution",
        datasetId: "abcd1234"
      },
      {
        dataset: "USA Demographic Dataset",
        status: "error",
        datasetId: "abcd1234"
      }
    ]
  })
};
</script>
