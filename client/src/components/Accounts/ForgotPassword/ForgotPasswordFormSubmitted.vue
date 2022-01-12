<template>
  <v-row>
    <v-col offset-md="2" cols="10" offset-sm="1">
      <h1 class="title-size-1 mb-1">Check your inbox</h1>
    </v-col>
    <v-col offset-md="2" md="5" offset-sm="1" sm="8">
      <p class="mb-0">
        We just sent you an email with a link to change your password:
      </p>
      <a
          class="font-weight-bold text-decoration-none"
          :href="`mailto:${email}`"
      >{{ email }}</a
      >
      <p class="my-8">
        If you don’t receive it within 5 minutes, please
        <span class="font-weight-bold">check your spam folder</span> or
        <span
            class="font-weight-bold primary--text pointer"
            @click="handleResendEmail"
        >resend the email</span
        >. If you’re still having issues receiving the email, please contact us
        at
        <a
            class="font-weight-bold text-decoration-none"
            href="mailto:info@opendp.org"
        >info@opendp.org</a
        >
      </p>
      <Button
          label="Back to log in"
          color="primary"
          :class="{ 'width100 mb-10': $vuetify.breakpoint.xsOnly }"
          :click="() => $router.push(NETWORK_CONSTANTS.LOGIN.PATH)"
      />
    </v-col>
  </v-row>
</template>

<script>
import Button from "../../DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../../../router/NETWORK_CONSTANTS";

export default {
  components: {Button},
  name: "ForgotYourPasswordFormSubmitted",
  methods: {
    handleResendEmail: function () {
      //TODO: Implement the logic that resends the forgot password email
      alert("resend email!");
    }
  },
  data: () => ({
    //TODO: Change this email for the current one of the user
    email: "danny-fi@gmail.com",
    NETWORK_CONSTANTS
  })
};
</script>
