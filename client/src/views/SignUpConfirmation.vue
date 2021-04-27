<template>
  <div class="sign-up mt-5">
    <v-container :class="{ 'px-10': $vuetify.breakpoint.xsOnly }">
      <v-row>
        <v-col offset-md="2" offset-sm="1" sm="8" md="8">
          <h1 class="title-size-1">Check your inbox and confirm the account</h1>
          <p class="mb-0">
            <!-- We have sent a confirmation link to the following email address: -->
            We have sent a confirmation link to your email address.
          </p>
          <!--<span class="font-weight-bold primary--text">{{ email }} </span>-->
        </v-col>
      </v-row>
      <v-row>
        <v-col offset-md="2" offset-sm="1" sm="8" md="5">
          <p class="mt-2 mb-8">
            If you don’t receive it within 5 minutes, please
            <span class="font-weight-bold">check your spam folder</span> or
            <span
                class="font-weight-bold primary--text pointer"
                @click="handleResendEmail"
            >resend the email</span
            >. If you’re still having issues receiving the email, please contact
            us at
            <a
                class="font-weight-bold text-decoration-none"
                href="mailto:support@opendp.com"
            >support@opendp.com</a
            >
          </p>
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
import {mapState} from 'vuex';

export default {
  name: "SignUpConfirmation",
  created() {
    this.$store.dispatch('auth/fetchUser')
  },
  methods: {
    handleResendEmail: function () {
      //TODO: Implement the logic that resends the confirmation email
      alert("resend email!");
    }
  },
  data: () => ({}),
  computed: {
    ...mapState('auth', ['user']),
    email() {
      return (this.user) ? this.user.email : null
    }
  },
};
</script>
