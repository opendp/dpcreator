<template>
  <div>
    <h2 class="title-size-2 mb-4"><strong>2/2. </strong>Sign up</h2>
    <v-container>
      <v-row>
        <v-col md="6" class="pl-0">
          <v-form
              v-model="validSignUpForm"
              ref="signUpForm"
              @submit.prevent="handleFormSubmit"
          >
            <v-text-field
                v-model="username"
                label="Username"
                :rules="usernameRules"
                required
            ></v-text-field>
            <v-text-field
                v-model="email"
                label="Email"
                required
                :rules="emailRules"
                type="email"
            ></v-text-field>
            <v-text-field
                v-model="password"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showPassword ? 'text' : 'password'"
                name="input-10-1"
                label="Password"
                :rules="passwordRules"
                counter
                @click:append="showPassword = !showPassword"
            ></v-text-field>
            <span class="pl-6 d-block grey--text text--darken-2"
            >Your <strong>password</strong> must be at least 6 characters long
              and must contain letters, numbers and special characters. Cannot
              contain whitespace.</span
            >
            <v-text-field
                v-model="confirmPassword"
                :append-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showConfirmPassword ? 'text' : 'password'"
                :rules="[confirmPasswordVerification, ...confirmPasswordRules]"
                name="input-10-2"
                label="Confirm password"
                counter
                @click:append="showConfirmPassword = !showConfirmPassword"
            ></v-text-field>
            <v-btn
                class="mr-3 mt-10"
                color="primary"
                type="submit"
                :disabled="!validSignUpForm"
            >Create account
            </v-btn
            >
            <v-btn
                color="primary"
                class="mt-10"
                outlined
                @click="$router.push('/')"
            >Cancel
            </v-btn
            >
          </v-form>
          <div class="mt-10">
            <SocialLoginSeparator/>
            <v-row>
              <v-col>
                <SocialLoginButton
                    mdiIcon="mdi-google"
                    iconBgColor="#C53126"
                    label="Log in with Google"
                    labelBgColor="#F44336"
                    :handler="loginGoogle"
                />
                <SocialLoginButton
                    mdiIcon="mdi-github"
                    iconBgColor="#2E2E2E"
                    label="Log in with GitHub"
                    labelBgColor="#050505"
                    :handler="loginGithub"
                />
              </v-col>
            </v-row>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import SocialLoginButton from "../SocialLoginButton.vue";
import SocialLoginSeparator from "../SocialLoginSeparator.vue";

export default {
  components: {SocialLoginButton, SocialLoginSeparator},
  name: "SignUpForm",
  methods: {
    confirmPasswordVerification() {
      return this.password === this.confirmPassword || `Passwords don't match`;
    },
    checkIfNeedToAdjustPasswordConfirmation() {
      if (this.confirmPassword !== "") {
        this.$refs.signUpForm.validate();
      }
    },
    handleFormSubmit: function () {
      if (this.$refs.signUpForm.validate()) {
        // SIGN UP FORM LOGIC HERE //
        this.$router.push("/sign-up/confirmation");
      }
    },
    loginGoogle: function () {
      alert("login with Google!");
    },
    loginGithub: function () {
      alert("login with Github!");
    }
  },
  data: () => ({
    validSignUpForm: false,
    showPassword: false,
    showConfirmPassword: false,
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    usernameRules: [v => !!v || "A username is required"],
    emailRules: [
      v => !!v || "E-mail is required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ],
    passwordRules: [
      v => {
        const pattern = /[\s]+/;
        return !pattern.test(v) || "Your password can't contain whitespaces";
      },
      v =>
          (v || "").length >= 6 ||
          "Your password has to be at least 6 characters long",
      v => {
        const pattern = /[a-zA-Z]+/;
        return (
            pattern.test(v) || "Your password has to have at least one letter"
        );
      },
      v => {
        const pattern = /[0-9]+/;
        return (
            pattern.test(v) || "Your password has to have at least one number"
        );
      },
      v => {
        const pattern = /[\W]+/;
        return (
            pattern.test(v) ||
            "Your password has to have at least one special character"
        );
      }
    ],
    confirmPasswordRules: [v => !!v || "Please confirm your password"]
  })
};
</script>
