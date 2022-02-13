<template><!--
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
  -->
  <div id="password-reset-confirm-view">
    <v-container>
      <v-row>
        <v-col
            offset-md="2"
            offset-sm="1"
            sm="8"
            md="5"
            :class="{ 'px-10': $vuetify.breakpoint.xsOnly }"
        >
          <h1 class="title-size-1">Reset Password Confirm</h1>

          <ColoredBorderAlert type="error" v-if="resetError">

            <template v-slot:content>
              Form Error:
              <ul>
                <li v-for="item in errorMessage">
                  {{ item }}
                </li>
              </ul>
            </template>
          </ColoredBorderAlert>

          <template v-if="resetLoading">
            loading...
          </template>
          <template v-else-if="!resetCompleted">
            <v-form ref="passwordForm" v-model="validForm" @submit.prevent="submitPasswordReset">
              <v-text-field
                  v-model="inputs.password1"
                  type="password" id="password1"
                  :append-icon="showPassword1 ? 'mdi-eye' : 'mdi-eye-off'"
                  :type="showPassword1 ? 'text' : 'password'"
                  @click:append="showPassword1 = !showPassword1"
                  :rules="passwordRules"
                  placeholder="password">
              </v-text-field>
              <v-text-field
                  v-model="inputs.password2"
                  type="password" id="password2"
                  :append-icon="showPassword2 ? 'mdi-eye' : 'mdi-eye-off'"
                  :type="showPassword2 ? 'text' : 'password'"
                  @click:append="showPassword2 = !showPassword2"
                  :rules="passwordRules"
                  placeholder="confirm password">
              </v-text-field>


              <Button
                  data-test="submit reset password"
                  classes="mt-5"
                  color="primary"
                  :class="{
                'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly,
                'mr-2': $vuetify.breakpoint.smAndUp
              }"
                  type="submit"
                  :disabled="!validForm"
                  label="Reset Password"
              />
            </v-form>
          </template>
          <template v-else>
            Your password has been reset.
            <router-link to="/log-in">return to login page</router-link>
          </template>

        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import {mapState} from 'vuex';
import accountInformation from "@/data/accountInformation";
import ColoredBorderAlert from "@/components/DynamicHelpResources/ColoredBorderAlert";
import Button from "@/components/DesignSystem/Button.vue";

export default {
  components: {Button, ColoredBorderAlert},
  name: 'PasswordResetConfirm',
  data() {
    return {
      passwordRules: accountInformation.passwordRules,
      errorMessage: "",
      validForm: false,
      showPassword1: false,
      showPassword2: false,
      inputs: {
        password1: '',
        password2: '',
        uid: this.$route.params.uid,
        token: this.$route.params.token,
      },
    };
  },
  computed: mapState('password', [
    'resetCompleted',
    'resetError',
    'resetLoading',
  ]),
  methods: {
    submitPasswordReset() {
      if (this.$refs.passwordForm.validate()) {
        console.log('submittinng')
        this.$store.dispatch('password/resetPassword', this.inputs)
            .then((resp) => {
            }).catch((error) => {
          console.log('error: ' + JSON.stringify(error))
          let msg = []
          Object.keys(error).forEach(function (k) {
            console.log(k + ' - ' + error[k]);
            msg.push(k + ' - ' + error[k])
          });
          this.errorMessage = msg
        })
      }
    }
  }

};
</script>
