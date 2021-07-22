<template>
  <div
      class="terms-and-conditions mt-5 mb-10"
      :class="{
      'px-5': $vuetify.breakpoint.xsOnly
    }"
  >
    <v-container>
      <v-row v-if="isTermsAccepted && currentTerms">
        <v-col offset-sm="1" sm="10" offset-md="2" cols="12" md="6">
          <h1 class="title-size-1">Terms of use</h1>
          <div v-html="currentTerms.description">
          </div>
          <template>
            <p class="grey--text text--darken-2">Last updated: {{ currentTerms.created }}</p>
          </template>
        </v-col>
      </v-row>
      <v-row v-if="!isTermsAccepted && currentTerms">
        <v-col offset-sm="1" sm="10" offset-md="2" cols="12" md="6">
          <ShadowBoxWithScroll>
            <template v-slot:scrollable-area>
              <span v-html="currentTerms.description"></span>
            </template>
            <template v-slot:actions>
              <Checkbox
                  data-test="confirmTermsCheckbox"
                  :value.sync="confirmTerms"
                  text="I have read and agree to the Terms of Service."
                  v-on:update:value="handleUpdate($event)"
              />
            </template>

          </ShadowBoxWithScroll>

          <Button
              :disabled="!confirmTerms"
              classes="mt-6"
              :class="{
        'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly,
        'mr-2': $vuetify.breakpoint.smAndUp
      }"
              color="primary"
              :click="() => $router.push(NETWORK_CONSTANTS.WELCOME.PATH)"
              label="Continue"
          />
        </v-col>
      </v-row>
    </v-container>
    <template v-if="confirmTerms">terms confirmed!</template>
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
      this.$store.dispatch('auth/setCurrentTerms')
      //  this.$store.dispatch('auth/setTermsLog',this.user.objectId)
    ]).then(() => this.loading = false)

  },
  computed: {
    ...mapState('auth', ['currentTerms', 'user']),
    ...mapGetters('auth', ['isTermsAccepted'])
  },
  data: () => ({
    loading: true,
    confirmTerms: false,
    NETWORK_CONSTANTS
  }),
  methods: {
    handleUpdate(accepted) {
      if (!this.loading) {
        console.log('user:' + this.user.objectId)
        console.log('termsId:' + this.currentTerms.objectId)
        console.log('received event: ' + accepted)
        if (accepted && this.user) {
          this.$store.dispatch('auth/acceptTerms', {
            user: this.user.objectId,
            termsOfAccess: this.currentTerms.objectId
          })
        }
      }

    }
  }
};
</script>
