<template>
  <div class="log-in mt-16">
    <v-container>
      <v-row>
        <v-col offset-md="2" md="4">
          <h1 class="title-size-1">Log in</h1>
          <v-form v-model="validLoginForm">
            <v-text-field
                v-model="inputs.username"
                label="Username"
                required
                type="text"
            ></v-text-field>
            <v-text-field
                v-model="inputs.password"
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
                  @click="login(inputs)"
              >Log in
              </v-btn
              >
              <v-btn color="primary" outlined @click="$router.push('/')"
              >Cancel
              </v-btn
              >
            </div>
            <v-alert dense outlined type="error" v-show="error">
              An error occurred while processing your request.
              <ul>
                <li v-for="err in loginErrors">{{ err }}</li>
              </ul>
            </v-alert>
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
import {mapState} from 'vuex';

export default {
  name: "Login",
  components: {SocialLoginButton, SocialLoginSeparator},
  computed: {
    ...mapState('auth', ['error', 'user']),
    ...mapState('dataverse', ['handoffId']),
    loginErrors() {
      let errs = [];
      if (this.errorMessage != null) {
        if (this.errorMessage['non_field_errors'] != null)
          errs = errs.concat(this.errorMessage['non_field_errors']);
      }
      return errs;
    },
    error() {
      return this.errorMessage != null;
    }
  },
  methods: {
    login: function ({username, password}) {
      this.errorMessage = null;
      this.$store.dispatch('auth/login', {username, password})
          .catch((data) => {
            this.errorMessage = data;
          })
          .then(() => {
            if (!this.error) {
              this.checkDataverseUser();
              this.$router.push('/welcome');
            }
          })
          .catch((data) => {
            console.log(data);
            this.errorMessage = data
          });

    },
    loginGoogle: function () {
      alert("login with Google!");
    },
    loginGithub: function () {
      alert("login with Github!");
    },
    checkDataverseUser() {
      if (this.handoffId) {
        this.$store.dispatch('auth/fetchUser')
            .then(() => {
              this.$store.dispatch('dataverse/updateDataverseUser', this.user['object_id'], this.handoffId)
                  .catch(({data}) => console.log("error: " + data)).then(({data}) => console.log(data))
            })
      }
    }

  },
  data: () => ({
    errorMessage: null,
    googleSignInParams: {
      client_id: '725082195083-1srivl3ra9mpc1q5ogi7aur17vkjuabg.apps.googleusercontent.com',
    },
    validLoginForm: false,
    showPassword: false,
    inputs: {
      username: '',
      password: '',
    },
    emailRules: [
      v => !!v || "E-mail is required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ],
    passwordRules: [v => !!v || "Password is required"]
  })
};
</script>
