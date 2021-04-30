<template>
  <div class="welcome">
    <EventSuccessAlert
        text="Account activated successfully."
        queryParam="accountActivated"
    />
    <v-container>
      <v-row>
        <v-col offset-sm="1" offset-md="0" sm="10" md="12">
          <!-- TODO: Change this label with the name of the current logged user -->
          <h1 class="title-size-1">Welcome, {{ username }}</h1>
          <ColoredBorderAlert type="warning" v-if="$vuetify.breakpoint.xsOnly">
            <template v-slot:content>
              If you want to start or continue the process you have to
              <strong>use the desktop version of the app.</strong>
            </template>
          </ColoredBorderAlert>
          <CreateDPStatistics v-bind:fileInfo="fileInfo"/>
          <h2
              class="title-size-2 font-weight-bold mt-16"
              :class="{
              'px-4': $vuetify.breakpoint.xsOnly
            }"
          >
            My Data
          </h2>
          <MyDataTable
              :class="{
              'my-7': $vuetify.breakpoint.xsOnly,
              'my-5': $vuetify.breakpoint.smAndUp
            }"
              :datasets="variables"
              :paginationVisible="false"
              :itemsPerPage="5"
          />
          <Button
              color="primary"
              outlined
              :class="{
              'width100 mx-auto d-block mt-10': $vuetify.breakpoint.xsOnly
            }"
              classes="font-weight-bold mt-5"
              :click="() => $router.push(NETWORK_CONSTANTS.MY_DATA.PATH)"
              label="See all my datasets"
          />
        </v-col>
      </v-row>
    </v-container>
    <SupportBanner/>
  </div>
</template>

<script>
import Button from "../components/DesignSystem/Button.vue";
import ColoredBorderAlert from "../components/DynamicHelpResources/ColoredBorderAlert.vue";
import EventSuccessAlert from "../components/Home/EventSuccessAlert.vue";
import MyDataTable from "../components/MyData/MyDataTable.vue";
import SupportBanner from "../components/SupportBanner.vue";
import CreateDPStatistics from "../components/Welcome/CreateDPStatistics.vue";
import NETWORK_CONSTANTS from "../router/NETWORK_CONSTANTS";
import {mapGetters, mapState} from 'vuex';

export default {
  name: "Welcome",
  components: {
    CreateDPStatistics,
    MyDataTable,
    SupportBanner,
    EventSuccessAlert,
    Button,
    ColoredBorderAlert
  },

  created() {
    this.$store.dispatch('auth/fetchUser')
  },
  computed: {
    ...mapGetters('auth', ['isAuthenticated']),
    ...mapState('auth', ['user']),
    ...mapState('dataverse', ['fileInfo']),
    username() {
      return (this.user) ? this.user.username : null
    }
  },
  data: () => ({
    variables: [
      {
        dataset: "California Demographic Dataset",
        status: "in_progress",
        remainingTime: "Expired",
        datasetId: "exampleInProgress"
      },
      {
        dataset: "California Demographic Dataset",
        status: "in_progress",
        remainingTime: "10h",
        datasetId: "exampleInProgress"
      },
      {
        dataset: "Tokio Demographic Dataset",
        status: "in_execution",
        remainingTime: "10h 30m",
        datasetId: "exampleInExecution"
      },
      {
        dataset: "Tokio Demographic Dataset",
        status: "error",
        remainingTime: "-",
        datasetId: "exampleError"
      },
      {
        dataset: "Tokio Demographic Dataset",
        status: "completed",
        remainingTime: "-",
        datasetId: "exampleCompleted"
      }
    ],
    NETWORK_CONSTANTS
  })
};
</script>
