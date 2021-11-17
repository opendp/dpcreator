<template>
  <div class="my-profile mt-5">
    <EventSuccessAlert queryParam="saved" text="Changes saved"/>

    <v-container
        class="py-5"
        :class="{
        'px-10': $vuetify.breakpoint.xsOnly
      }"
    >
      <v-row>
        <v-col offset-md="2" md="5">
          <h1 class="title-size-1">My Profile</h1>
          <h2 class="title-size-2 mt-8">Edit account information</h2>
          <v-form @submit.prevent="handleEditAccountInformation">
            <v-text-field
                v-model="username"
                data-test="username"
                label="Username"
                required
            ></v-text-field>
            <v-text-field
                v-model="email"
                label="Email"
                required
                :rules="emailRules"
                type="email"
            ></v-text-field>
            <div class="mt-5 mb-10">
              <Button
                  type="submit"
                  color="primary"
                  label="Save changes"
                  :class="{
                  'width80 mx-auto d-block mb-2': $vuetify.breakpoint.xsOnly,
                  'mr-2 mb-2': $vuetify.breakpoint.smAndUp
                }"
              />
              <Button
                  color="primary"
                  outlined
                  :click="() => $router.push(NETWORK_CONSTANTS.HOME.PATH)"
                  :class="{
                  'width80 mx-auto d-block': $vuetify.breakpoint.xsOnly,
                  'mb-2': $vuetify.breakpoint.smAndUp
                }"
                  label="Cancel"
              />
            </div>
          </v-form>
          <h2 class="title-size-2 mt-10">Change password</h2>
          <v-form @submit.prevent="handleChangePassword">
            <v-text-field
                v-model="password"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showPassword ? 'text' : 'password'"
                name="input-10-1"
                label="Current password"
                @click:append="showPassword = !showPassword"
            ></v-text-field>
            <v-text-field
                v-model="newPassword"
                :append-icon="showNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showNewPassword ? 'text' : 'password'"
                name="input-10-2"
                label="New password"
                :rules="passwordRules"
                counter
                @click:append="showNewPassword = !showNewPassword"
            ></v-text-field>
            <span
                class="d-block grey--text text--darken-2"
                :class="{
                'pl-6': $vuetify.breakpoint.smAndUp
              }"
            >Your <strong>password</strong> must be at least 6 characters long
              and must contain letters, numbers and special characters. Cannot
              contain whitespace.</span
            >
            <v-text-field
                v-model="confirmNewPassword"
                :append-icon="showConfirmNewPassword ? 'mdi-eye' : 'mdi-eye-off'"
                :type="showConfirmNewPassword ? 'text' : 'password'"
                :rules="[confirmNewPasswordRules]"
                name="input-10-3"
                label="Confirm new password"
                counter
                @click:append="showConfirmNewPassword = !showConfirmNewPassword"
            ></v-text-field>
            <div class="mt-5 mb-10">
              <Button
                  type="submit"
                  color="primary"
                  label="Save changes"
                  :class="{
                  'width80 mx-auto d-block mb-2': $vuetify.breakpoint.xsOnly,
                  'mr-2 mb-2': $vuetify.breakpoint.smAndUp
                }"
              />
              <Button
                  color="primary"
                  outlined
                  :click="() => $router.push(NETWORK_CONSTANTS.HOME.PATH)"
                  label="Cancel"
                  :class="{
                  'width80 mx-auto d-block mb-2': $vuetify.breakpoint.xsOnly,
                  'mb-2': $vuetify.breakpoint.smAndUp
                }"
              />
            </div>
          </v-form>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Button from "../components/DesignSystem/Button.vue";
import EventSuccessAlert from "../components/Home/EventSuccessAlert.vue";
import NETWORK_CONSTANTS from "../router/NETWORK_CONSTANTS";
import {mapState} from "vuex";
import auth from '../api/auth';

export default {
  name: "MyProfile",
  components: {Button, EventSuccessAlert},
  computed: {
    ...mapState('auth', ['user']),
  },
  created: function () {
    this.username = this.user.username
    this.email = this.user.email
  },
  methods: {
    confirmNewPasswordRules() {
      return (
          this.newPassword === this.confirmNewPassword || `Passwords don't match`
      );
    },
    handleEditAccountInformation() {
      this.$store.dispatch('auth/changeUsername', this.username)
      this.$router.push(`${NETWORK_CONSTANTS.MY_PROFILE.PATH}?saved=true`);
    },
    handleChangePassword() {
      auth.changePassword(this.password, this.newPassword, this.confirmNewPassword)
          .then(() => {
                this.password = "",
                    this.newPassword = "",
                    this.confirmNewPassword = "",
                    this.$router.push(`${NETWORK_CONSTANTS.MY_PROFILE.PATH}?saved=true`);
              }
          )

    }
  },

  data: () => ({
    showPassword: false,
    showNewPassword: false,
    showConfirmNewPassword: false,
    username: "",
    email: "",
    password: "",
    newPassword: "",
    confirmNewPassword: "",
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
    NETWORK_CONSTANTS
  })
};
</script>
