<template>
  <div class="sign-up mt-16">
    <v-container>
      <v-row>
        <v-col offset-md="2" md="8">
          <h1 class="title-size-1">Check your inbox and confirm the account</h1>
          <p class="mb-0">
            We have sent a confirmation link to the following email address:
          </p>
          <a
              class="font-weight-bold text-decoration-none"
              :href="`mailto:${email}`"
          >{{ email }}</a
          >
        </v-col>
      </v-row>
      <v-row>
        <v-col offset-md="2" md="5">
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
export default {
  name: "SignUpConfirmation",
  methods: {
    handleResendEmail: function () {
      alert("resend email!");
    }
  },
  data: () => ({
    email: "danny-fi@gmail.com"
  })
};
</script>
