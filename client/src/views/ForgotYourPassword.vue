<template>
  <div class="forgot-your-password">
    <v-container
        :class="{
        'px-10 mt-5': $vuetify.breakpoint.xsOnly
      }"
    >
      <ForgotPasswordForm
          :submitted.sync="forgotPasswordFormSubmitted"
          :email.sync="userEmail"
          v-if="!forgotPasswordFormSubmitted"
      />
      <ForgotPasswordFormSubmitted :email="userEmail" v-else/>
    </v-container>
  </div>
</template>

<script>
import ForgotPasswordForm from "../components/Accounts/ForgotPassword/ForgotPasswordForm.vue";
import ForgotPasswordFormSubmitted from "../components/Accounts/ForgotPassword/ForgotPasswordFormSubmitted.vue";
import {mapState} from "vuex";
export default {
  components: {ForgotPasswordForm, ForgotPasswordFormSubmitted},
  name: "ForgotYourPassword",
  computed: {
    ...mapState('auth', ['user']),
  },
  data: () => ({
    userEmail: "",
    forgotPasswordFormSubmitted: false
  })
};
</script>
