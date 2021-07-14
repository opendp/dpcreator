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
          <h1 class="title-size-1">Terms of use</h1>
          <template v-if="!loading"> {{ currentTerms.description }}
          </template>
          <template v-if="!loading">
            <p class="grey--text text--darken-2">{{ currentTerms.created }}</p>
          </template>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import {mapGetters, mapState} from "vuex";

export default {
  name: "TermsAndConditions",
  created() {
    this.$store.dispatch('auth/setCurrentTerms')
        .then(() => {
          this.loading = false
        })

  },
  computed: {
    ...mapState('auth', ['currentTerms']),
  },
  data: () => ({
    loading: true,
  })
};
</script>
