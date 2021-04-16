<template>
  <div class="forgot-your-password">
    <v-container
        :class="{
        'px-10 mt-5': $vuetify.breakpoint.xsOnly
      }"
    >
      <ForgotPasswordForm
          :submitted.sync="forgotPasswordFormSubmitted"
          v-if="!forgotPasswordFormSubmitted"
      />
      <ForgotPasswordFormSubmitted v-else/>
    </v-container>
  </div>
</template>

<script>
import ForgotPasswordForm from "../components/Accounts/ForgotPassword/ForgotPasswordForm.vue";
import ForgotPasswordFormSubmitted from "../components/Accounts/ForgotPassword/ForgotPasswordFormSubmitted.vue";
export default {
  components: {ForgotPasswordForm, ForgotPasswordFormSubmitted},
  name: "ForgotYourPassword",
  data: () => ({
    forgotPasswordFormSubmitted: false
  })
};
</script>
