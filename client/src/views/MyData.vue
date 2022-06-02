<template>
  <div class="my-data">
    <v-container>
      <v-sheet rounded="lg">
        <v-container
            :class="{
            'px-0': $vuetify.breakpoint.xsOnly
          }"
        >
          <h1
              class="title-size-1"
              :class="{
              'px-5': $vuetify.breakpoint.xsOnly
            }"
          >
            My Data
          </h1>
          <v-row
              :class="{
              'px-5': $vuetify.breakpoint.xsOnly
            }"
          >
            <v-col cols="12" sm="7">
              <p>
                Check your differential privacy releases and pending processes.
                Click on View details to know more about them and their
                statuses.
              </p>
            </v-col>
            <v-col cols="12" v-if="$vuetify.breakpoint.xsOnly">
              <ColoredBorderAlert type="warning">
                <template v-slot:content>
                  If you want to start or continue the process you have to
                  <strong>use the desktop version of the app.</strong>
                </template>
              </ColoredBorderAlert>
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
          <v-row justify="end">
            <v-spacer/>
            <v-col class="text-right">
              <upload-files></upload-files>
            </v-col>
          </v-row>
          <MyDataTable
              v-if="!loading"
              :class="{ 'my-5': $vuetify.breakpoint.smAndUp }"
              :datasets="getMyDataList"
              :searchTerm="search"
              :itemsPerPage="5"
          />
        </v-container>
      </v-sheet>
    </v-container>
    <SupportBanner/>
  </div>
</template>

<script>
import ColoredBorderAlert from "../components/DynamicHelpResources/ColoredBorderAlert.vue";
import UploadFiles from "../components/DesignSystem/UploadFiles";

import MyDataTable from "../components/MyData/MyDataTable.vue";
import SupportBanner from "../components/SupportBanner.vue";
import {mapGetters} from "vuex";

export default {
  name: "MyData",
  components: {MyDataTable, ColoredBorderAlert, SupportBanner, UploadFiles},
  created() {
    this.$store.dispatch('dataset/setDatasetList')
        .then(() => {
          this.loading = false
        })

  },
  computed: {

    ...mapGetters('dataset', ['getMyDataList'])
  },
  data: () => ({
    loading: true,
    search: "",

  })
};
</script>
