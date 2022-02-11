<template>
  <div class="sign-up mt-5">
    <v-container :class="{ 'px-10': $vuetify.breakpoint.xsOnly }">
      <v-row>
        <v-col offset-md="2" offset-sm="1" sm="8" md="8">
          <h1 class="title-size-1">Verify Email</h1>
          <p class="mb-0">
            <template v-if="activationLoading">loading...</template>
            <template v-else-if="activationError">An error occured.</template>
            <template v-else-if="activationCompleted">
              Account activation successful.
              <router-link v-if="!isAuthenticated" to="/log-in">
                Click here to sign in.
              </router-link>
            </template>
          </p>
          <!--<span class="font-weight-bold primary--text">{{ email }} </span>-->
        </v-col>
      </v-row>

    </v-container>
  </div>

</template>

<style lang="scss">
.sign-up {
  .v-stepper {
    box-shadow: unset;
  }

  .v-card__text {
    max-height: 20vh;
    overflow: auto;
  }
}
</style>

<script>
import {
  mapActions,
  mapGetters,
  mapState,
} from 'vuex';

export default {
  computed: {
    ...mapGetters('auth', ['isAuthenticated']),
    ...mapState('signup', [
      'activationCompleted',
      'activationError',
      'activationLoading',
    ]),
  },
  methods: mapActions('signup', [
    'activateAccount',
    'clearActivationStatus',
  ]),
  created() {
    this.activateAccount(this.$route.params);
  },
  beforeRouteLeave(to, from, next) {
    this.clearActivationStatus();
    next();
  },
};
</script>
