<template>
  <div class="log-in mt-5">
    <v-container>
      <h2
          class="title-size-2 mb-4"
          :class="{ 'ml-5': $vuetify.breakpoint.xsOnly }"
      >
        Mock DV Test
      </h2>
      <v-row>
        <v-col
            md="8"
            class="pl-0"
            :class="{ 'ml-5': $vuetify.breakpoint.xsOnly }"
        >
          <v-form
              v-model="validForm"
              ref="dvForm"
              @submit.prevent="handleFormSubmit"
          >
            <v-text-field id="site_url"
                          v-model="site_url"
                          label="site_url"
                          required
            ></v-text-field>
            <v-text-field
                v-model="token"
                label="token"
                required
            ></v-text-field>
            <v-text-field
                v-model="fileId"
                label="fileId"
                required
            ></v-text-field>
            <v-text-field
                v-model="datasetPid"
                label="datasetPid"
                required
            ></v-text-field>

            <Button
                id="postOpenDP"
                classes="mt-5"
                color="primary"
                :class="{
                'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly,
                'mr-2': $vuetify.breakpoint.smAndUp
              }"
                type="submit"
                :disabled="!validForm"
                label="Post to OpenDP"
            />

          </v-form>

          <div
              class="my-5"
              :class="{
              'text-center': $vuetify.breakpoint.xsOnly
            }"
          >

          </div>

        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Button from "../components/DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../router/NETWORK_CONSTANTS";
import dataverse from '../api/dataverse'
import {mapState} from 'vuex';

export default {
  name: "MockDV",
  components: {Button},
  computed: {
    ...mapState('auth', ['error', 'user']),
    ...mapState('dataverse', ['handoffId']),
  },
  methods: {
    handleFormSubmit: function () {
      dataverse.testHandoff(this.site_url, this.fileId, this.datasetPid, this.token)
    },


  },
  data: () => ({
    validForm: false,
    site_url: 'http://127.0.0.1:8000/dv-mock-api',
    fileId: '4164587',
    datasetPid: 'doi:10.7910/DVN/PUXVDH',
    token: 'shoefly-dont-bother-m3'

    // validForm: false,
    // site_url: 'https://dataverse.harvard.edu/',
    // fileId: '4498613',
    // datasetPid: 'doi:10.7910/DVN/VOB36N',
    // token: '<use harvard dv token>'
  })
};
</script>
