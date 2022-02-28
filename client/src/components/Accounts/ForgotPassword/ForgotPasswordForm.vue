<template>
  <v-row>
    <v-col offset-sm="1" offset-md="2" cols="12" md="10">
      <h1 class="title-size-1">Forgot password?</h1>
      <h2 class="title-size-2">
        We will send you an email to reset your password.
      </h2>
    </v-col>
    <v-col offset-sm="1" sm="8" offset-md="2" md="5">
      <v-form
          v-model="validForgotPasswordForm"
          ref="forgotPasswordForm"
          @submit.prevent="handleFormSubmit"
      >
        <v-text-field
            v-model="email"
            label="Email"
            required
            :rules="emailRules"
            type="email"
        ></v-text-field>

        <div class="my-10">
          <Button
              color="primary"
              :class="{
              'width80 mx-auto d-block mb-2': $vuetify.breakpoint.xsOnly,
              'mr-2': $vuetify.breakpoint.smAndUp
            }"
              :disabled="!validForgotPasswordForm"
              type="submit"
              label="Submit"
          />
          <Button
              color="primary"
              :class="{
              'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly
            }"
              outlined
              :click="() => $router.push(NETWORK_CONSTANTS.HOME.PATH)"
              label="Cancel"
          />
        </div>
      </v-form>
    </v-col>
  </v-row>
</template>

<style lang="scss" scoped>
.title-size-2 {
  @media screen and (max-width: 600px) {
    font-size: 1rem;
  }
}
</style>

<script>
import Button from "../../DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../../../router/NETWORK_CONSTANTS";
import auth from '../../../api/auth';

export default {
  components: {Button},
  name: "ForgotYourPasswordForm",

  methods: {
    handleFormSubmit: function () {
      if (this.$refs.forgotPasswordForm.validate()) {
        auth.sendAccountPasswordResetEmail(this.email)

        this.$emit("update:submitted", true);
        this.$emit("update:email", this.email)
      }
    }
  },
  data: () => ({
    validForgotPasswordForm: false,
    email: "",
    emailRules: [
      v => !!v || "E-mail is required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ],
    NETWORK_CONSTANTS
  })
};
</script>
