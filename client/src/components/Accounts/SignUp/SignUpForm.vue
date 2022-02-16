<template>
  <div>
    <h2
        class="title-size-2 mb-4"
        :class="{ 'ml-5': $vuetify.breakpoint.xsOnly }"
    >
      <strong>2/2. </strong>Sign up
    </h2>
    <v-container class="ml-0">
      <v-row>
        <v-col
            md="8"
            class="pl-0"
            :class="{ 'ml-5': $vuetify.breakpoint.xsOnly }"
        >
          <ColoredBorderAlert
              data-test="errorMessage"
              type="error" v-if="errorMessage!==null">
            <template v-slot:content>
              <ul>
                <li v-for="item in errorMessage">
                  {{ item }}
                </li>
              </ul>
            </template>
          </ColoredBorderAlert>
          <v-form
              v-model="validSignUpForm"
              ref="signUpForm"
              @submit.prevent="handleFormSubmit"
          >
            <v-text-field
                v-model="username"
                data-test="username"
                label="Username"
                :rules="usernameRules"
                required
            ></v-text-field>
            <v-text-field
                v-model="email"
                data-test="email"
                label="Email"
                required
                :rules="emailRules"
                type="email"
            ></v-text-field>
            <v-text-field
                v-model="password"
                data-test="password"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showPassword ? 'text' : 'password'"
                name="input-10-1"
                label="Password"
                :rules="passwordRules"
                counter
                @click:append="showPassword = !showPassword"
            ></v-text-field>
            <span
                id="password-hint"
                class="d-block grey--text text--darken-2 mb-5"
                :class="{ 'pl-6': $vuetify.breakpoint.smAndUp }"
            >Your <strong>password</strong> must be at least 6 characters long
              and must contain letters, numbers and special characters. Cannot
              contain whitespace.</span
            >
            <v-text-field
                v-model="confirmPassword"
                data-test="confirmPassword"
                :append-icon="showConfirmPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showConfirmPassword ? 'text' : 'password'"
                :rules="[confirmPasswordVerification, ...confirmPasswordRules]"
                name="input-10-2"
                label="Confirm password"
                counter
                @click:append="showConfirmPassword = !showConfirmPassword"
            ></v-text-field>
            <Button
                data-test="submit"
                classes="mt-5"
                color="primary"
                :class="{
                'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly,
                'mr-2': $vuetify.breakpoint.smAndUp
              }"
                type="submit"
                :disabled="!validSignUpForm"
                label="Create account"
            />
            <Button
                color="primary"
                classes="mt-5"
                :class="{ 'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly }"
                outlined
                :click="() => $router.push(NETWORK_CONSTANTS.HOME.PATH)"
                label="Cancel"
            />
          </v-form>
          <div class="mt-10 social-login">
            <SocialLoginSeparator/>
            <SocialLoginButton
                mdiIcon="mdi-google"
                iconBgColor="#C53126"
                label="Log in with Google"
                labelBgColor="#F44336"
                :handler="loginGoogle"
            />
          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style lang="scss" scoped>
#password-hint {
  @media screen and (max-width: 600px) {
    font-size: 0.875rem;
  }
}
</style>

<script>
import Button from "../../DesignSystem/Button.vue";
import SocialLoginButton from "../SocialLoginButton.vue";
import SocialLoginSeparator from "../SocialLoginSeparator.vue";
import NETWORK_CONSTANTS from "../../../router/NETWORK_CONSTANTS";
import {mapState, mapGetters} from "vuex";
import ColoredBorderAlert from "@/components/DynamicHelpResources/ColoredBorderAlert";

export default {
  components: {SocialLoginButton, SocialLoginSeparator, Button, ColoredBorderAlert},
  name: "SignUpForm",
  props: ["termsId"],
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
        let inputs = {
          username: this.username,
          password1: this.password,
          password2: this.confirmPassword,
          email: this.email,
        }
        this.$store.dispatch('signup/createAccount', inputs)
            .then((resp) => {
              console.log("returned from create acount, resp: " + JSON.stringify(resp))
              const openDPUserId = resp.data[0]
              if (this.handoffId) {
                this.$store.dispatch('dataverse/updateDataverseUser', openDPUserId, this.handoffId)
                    .then((dvUserObjectId) => {
                      this.$store.dispatch('dataverse/updateFileInfo', dvUserObjectId, this.handoffId)
                          .catch(({data}) => console.log("update file info error: " + data))
                    })
                    .catch((data) => {
                      console.log("update dataverse user error " + data)
                      this.errorMessage = data
                    });
              }
              this.$router.push(`${NETWORK_CONSTANTS.SIGN_UP.PATH}/confirmation`);
            }).catch((error) => {
          let msg = []
          Object.keys(error).forEach(function (k) {
            console.log(k + ' - ' + error[k]);
            msg.push(error[k][0])
          });
          this.errorMessage = msg
        })

      }
    },
    loginGoogle(access_token) {
      this.$store.dispatch('auth/googleLogin', access_token)
          .then(() => {
            this.processLogin();
          })
    },

    processLogin() {
      if (this.handoffId) {
        this.$store.dispatch('auth/fetchUser')
            .then((data) => {
              this.$store.dispatch('dataverse/updateDataverseUser', this.user.objectId, this.handoffId)
                  .then((dvUserObjectId) => {
                    this.$store.dispatch('dataverse/updateFileInfo', dvUserObjectId, this.handoffId)
                        .catch(({data}) => console.log("error: " + data))
                        .then(() => {
                          this.$router.push('/welcome')
                        })
                  })
                  .catch((data) => console.log(data))
              this.errorMessage = data
            })
            .catch((data) => {
              console.log(data)
              this.errorMessage = data
            });
      } else {
        if (this.errorMessage == null) {
          this.$router.push('/welcome')
        }
      }
    },

    loginGithub: function () {
      //TODO: Implement Login with Github logic here
      alert("login with Github!");
    }
  },
  computed: {
    ...mapState('signup', ['registrationCompleted',
      'registrationError',
      'registrationLoading']),
    ...mapState('dataverse', ['handoffId', 'dataverseUser']),
    ...mapState('auth', ['user']),


    registrationErrors() {
      let errs = [];
      if (this.errorMessage != null) {
        if (this.errorMessage['password1'] != null)
          errs = errs.concat(this.errorMessage['password1'])
        if (this.errorMessage['email'] != null)
          errs = errs.concat(this.errorMessage['email']);
        if (this.errorMessage['non_field_errors'] != null)
          errs = errs.concat(this.errorMessage['non_field_errors']);
      }
      return errs;
    }
  },
  data: () => ({
    validSignUpForm: false,
    showPassword: false,
    showConfirmPassword: false,
    errorMessage: null,
    googleSignInParams: {
      client_id: process.env.GOOGLE_CLIENT,
    },

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
    confirmPasswordRules: [v => !!v || "Please confirm your password"],
    NETWORK_CONSTANTS
  })
};
</script>
