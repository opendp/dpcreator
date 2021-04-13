<template>
  <div class="log-in mt-16">
    <v-container>
      <v-row>
        <v-col offset-md="2" md="4">
          <h1 class="title-size-1">Log in</h1>
          <v-form v-model="validLoginForm">
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
                @click:append="showPassword = !showPassword"
            ></v-text-field>
            <router-link to="/forgot-your-password" class="text-decoration-none"
            >Forgot your password?
            </router-link
            >
            <div class="mt-14 mb-7">
              <v-btn
                  class="mr-3"
                  color="primary"
                  :disabled="!validLoginForm"
                  @click="handleLogin"
              >Log in
              </v-btn
              >
              <v-btn color="primary" outlined @click="$router.push('/')"
              >Cancel
              </v-btn
              >
            </div>
          </v-form>
          <div class="my-5">
            <span
            >New user?
              <router-link
                  to="/sign-up"
                  class="text-decoration-none font-weight-bold"
              >Create account</router-link
              ></span
            >
          </div>
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
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import SocialLoginButton from "../components/Accounts/SocialLoginButton.vue";
import SocialLoginSeparator from "../components/Accounts/SocialLoginSeparator.vue";

export default {
  name: "MyData",
  components: {SocialLoginButton, SocialLoginSeparator},
  methods: {
    handleLogin: function () {
      localStorage.setItem("loggedUser", true);
      this.$router.push("/welcome");
    },
    loginGoogle: function () {
      alert("login with Google!");
    },
    loginGithub: function () {
      alert("login with Github!");
    }
  },
  data: () => ({
    validLoginForm: false,
    showPassword: false,
    email: "",
    password: "",
    emailRules: [
      v => !!v || "E-mail is required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ],
    passwordRules: [v => !!v || "Password is required"]
  })
};
</script>
