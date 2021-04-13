<template>
  <v-row>
    <v-col offset-md="2" cols="10">
      <h1 class="title-size-1">Forgot password?</h1>
      <h2 class="title-size-2">
        We will send you an email to reset your password.
      </h2>
    </v-col>
    <v-col offset-md="2" md="5">
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
          <v-btn
              class="mr-3"
              color="primary"
              :disabled="!validForgotPasswordForm"
              type="submit"
          >Submit
          </v-btn
          >
          <v-btn color="primary" outlined @click="$router.push('/')"
          >Cancel
          </v-btn
          >
        </div>
      </v-form>
    </v-col>
  </v-row>
</template>

<script>
export default {
  name: "ForgotYourPasswordForm",
  methods: {
    handleFormSubmit: function () {
      if (this.$refs.forgotPasswordForm.validate()) {
        // RESET PASSWORD LOGIC HERE //
        this.$emit("update:submitted", true);
      }
    }
  },
  data: () => ({
    validForgotPasswordForm: false,
    email: "",

    emailRules: [
      v => !!v || "E-mail is required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ]
  })
};
</script>
