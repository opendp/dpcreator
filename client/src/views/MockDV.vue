<template>
  <div class="log-in mt-5">
    <v-container>
      <v-row>
        <v-col
            offset-md="2"
            offset-sm="1"
            sm="8"
            md="5"
            :class="{ 'px-10': $vuetify.breakpoint.xsOnly }"
        >
          <h1 class="title-size-1">Mock Dataverse Request</h1>
          <v-form>


            <Button
                color="primary"
                :class="{
                  'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly
                }"
                outlined
                :click="testHandoff"
                label="Test Handoff"
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
    testHandoff: function () {
      dataverse.testHandoff()
    },


  },
  data: () => ({
    validLoginForm: false,
    showPassword: false,
    inputs: {
      username: '',
      password: '',
    },

    NETWORK_CONSTANTS
  })
};
</script>
