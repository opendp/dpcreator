<template>
  <div
      class="terms-and-conditions mt-5 mb-10"
      :class="{
      'px-5': $vuetify.breakpoint.xsOnly
    }"
  >
    <v-container>
      <v-row>
        <v-col offset-sm="1" sm="10" offset-md="2" cols="12" md="6">
          <ShadowBoxWithScroll v-if="currentTerms">
            <template v-slot:scrollable-area>
              <span v-html="currentTerms.description"></span>
            </template>
            <template v-slot:actions>

            </template>

          </ShadowBoxWithScroll>


        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import {mapGetters, mapState} from "vuex";
import ShadowBoxWithScroll from "../components/DesignSystem/Boxes/ShadowBoxWithScroll.vue";
import Button from "../components/DesignSystem/Button.vue";
import Checkbox from "../components/DesignSystem/Checkbox.vue";
import NETWORK_CONSTANTS from "../router/NETWORK_CONSTANTS";

export default {
  components: {ShadowBoxWithScroll, Checkbox, Button},
  name: "TermsAndConditions",
  created() {
    Promise.all([
      this.$store.dispatch('auth/fetchCurrentTerms'),
    ]).then(() => this.loading = false)

  },
  computed: {
    ...mapState('auth', ['currentTerms', 'user']),
  },


};
</script>
