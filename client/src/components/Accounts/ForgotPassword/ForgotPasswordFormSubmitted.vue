<template>
  <v-row>
    <v-col offset-md="2" cols="10">
      <h1 class="title-size-1 mb-1">Check your inbox</h1>
    </v-col>
    <v-col offset-md="2" md="5">
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
            href="mailto:support@opendp.com"
        >support@opendp.com</a
        >
      </p>
      <v-btn color="primary" @click="$router.push('/log-in')"
      >Back to log in
      </v-btn
      >
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: "ForgotYourPasswordFormSubmitted",
  data: () => ({
    email: "danny-fi@gmail.com"
  })
};
</script>
