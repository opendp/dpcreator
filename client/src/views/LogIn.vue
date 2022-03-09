<template>
  <div class="log-in mt-5">
    <v-container>
      <v-row>
        <v-col
            offset-md="2"
            offset-sm="1"
            sm="8"
            md="5"
            :class="{ 'px-10': $vuetify.breakpoint.xsOnly }"
        >
          <h1 class="title-size-1">Log in</h1>
          <ColoredBorderAlert type="error" v-if="errorMessage!==null">
            <template v-slot:content>
              {{ errorMessage.non_field_errors[0] }}
            </template>
          </ColoredBorderAlert>
          <v-form data-test="login form" v-model="validLoginForm">
            <v-text-field
                data-test="username"
                v-model="inputs.username"
                label="Username"
                required
                type="text"
            ></v-text-field>
            <v-text-field
                data-test="password"
                v-model="inputs.password"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showPassword ? 'text' : 'password'"
                name="input-10-1"
                label="Password"
                :rules="passwordRules"
                @click:append="showPassword = !showPassword"
            ></v-text-field>
            <router-link
                :to="NETWORK_CONSTANTS.FORGOT_YOUR_PASSWORD.PATH"
                class="text-decoration-none"
            >Forgot your password?
            </router-link
            >
            <div class="mt-14 mb-7">
              <Button
                  data-test="Log in"
                  :class="{
                  'mb-2 width80 mx-auto d-block': $vuetify.breakpoint.xsOnly,
                  'mr-2': $vuetify.breakpoint.smAndUp
                }"
                  color="primary"
                  :disabled="!validLoginForm"
                  :click="handleLogin"
                  label="Log In"
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
          <div
              class="my-5"
              :class="{
              'text-center': $vuetify.breakpoint.xsOnly
            }"
          >
            <span
            >New user?
              <router-link
                  :to="NETWORK_CONSTANTS.SIGN_UP.PATH"
                  class="text-decoration-none font-weight-bold"
              >Create account</router-link
              ></span
            >
          </div>
          <div class="mb-10 social-login">
            <SocialLoginSeparator/>
            <SocialLoginButton
                mdiIcon="mdi-google"
                iconBgColor="#C53126"
                label="Log in with Google"
                labelBgColor="#F44336"
                :handler="handleGoogle"
            />

          </div>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import SocialLoginButton from "../components/Accounts/SocialLoginButton.vue";
import SocialLoginSeparator from "../components/Accounts/SocialLoginSeparator.vue";
import Button from "../components/DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../router/NETWORK_CONSTANTS";
import {mapState, mapGetters} from 'vuex';
import ColoredBorderAlert from "@/components/DynamicHelpResources/ColoredBorderAlert";

export default {
  name: "MyData",
  components: {SocialLoginButton, SocialLoginSeparator, Button, ColoredBorderAlert},
  computed: {
    ...mapState('auth', ['error', 'user', 'currentTerms']),
    ...mapGetters('auth', ['isTermsAccepted', 'isCurrentTermsAccepted']),
    ...mapState('dataverse', ['handoffId']),
  },
  methods: {
    handleLogin: function () {
      // Format loginParams, including the handoffId (which can be null)
      let loginParams = Object.assign({}, this.inputs);
      loginParams.handoffId = this.handoffId
      this.errorMessage = null;
      this.$store.dispatch('auth/login', loginParams)
          .then((data) => {
             this.processLogin();
          })
          .catch((data) => {
            this.errorMessage = data
          })
    },
    handleGoogle(access_token) {
      this.$store.dispatch('auth/googleLogin', access_token)
          .then(() => {
            this.processLogin();
          })
    },
    routeToNextPage(defaultPath) {
      Promise.all([
        this.$store.dispatch('auth/fetchCurrentTerms'),
        this.$store.dispatch('auth/fetchTermsLog')
      ]).then(() => {
        // If no terms have been accepted, this means it is the first time logging in,
        // and terms were accepted at the time of account creation.  So set the terms as accepted
        if (!this.isTermsAccepted) {
          this.$store.dispatch('auth/acceptTerms', {
            userId: this.user.objectId,
            termsOfAccessId: this.currentTerms.objectId
          })
          this.routeToNextPage(defaultPath)
        } else if (this.isCurrentTermsAccepted) {
          // Go back to redirect page, or default page
          this.$router.replace(sessionStorage.getItem('redirectPath') || defaultPath);
          //Cleanup redirectPath
          sessionStorage.removeItem('redirectPath');
        } else {
          this.$router.push(NETWORK_CONSTANTS.TERMS_AND_CONDITIONS.PATH)
        }
      })
    },
    processDVFileInfo(handoffId) {
      return this.$store.dispatch('dataverse/updateFileInfo',
          {openDPUserId: this.user.objectId, handoffId: handoffId})
          .catch(({data}) => this.errorMessage = data)
          .then(() => {
            this.routeToNextPage(NETWORK_CONSTANTS.WELCOME.PATH)
          })
    },
    processLogin() {
      this.$store.dispatch('auth/fetchUser')
          .then((data) => {
            if (this.handoffId !== null) {
              // the Vuex store handoffId exists, which means the user
              // has just come from Dataverse, so update the DVUser and DVFileInfo
              // based on the handoff parameters.
              this.$store.dispatch('dataverse/updateDataverseUser', this.user.objectId, this.handoffId)
                  .then(() => {
                    this.processDVFileInfo(this.handoffId)
                  })
            } else if (this.user.handoffId !== null) {
              // If the user comes from dataverse and creates an account, then original handoffId
              // is stored in the user object. So when the user logs in after verifying the account,
              // create the DVFile here using the handoffId
              // (No need to create or update the DVUser because it was created when the account was created.)
              this.processDVFileInfo(this.user.handoffId)
            } else {
              this.routeToNextPage(NETWORK_CONSTANTS.MY_DATA.PATH)
            }

          })
          .catch((data) => {
            console.log(data)
            this.errorMessage = data
          });
    }
  },
  data: () => ({
    validLoginForm: false,
    showPassword: false,
    errorMessage: null,
    inputs: {
      username: '',
      password: '',
      //handoffId: this.handoffId,
    },
    emailRules: [
      v => !!v || "E-mail is required",
      v => /.+@.+\..+/.test(v) || "E-mail must be valid"
    ],
    passwordRules: [v => !!v || "Password is required"],
    NETWORK_CONSTANTS
  })
};
</script>
