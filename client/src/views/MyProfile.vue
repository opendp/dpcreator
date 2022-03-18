<template>
  <div class="my-profile mt-5">
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
          <template v-if="editUserError">
            <ColoredBorderAlert type="error" v-if="errorMessage">
              <template v-slot:content>
                <ul>
                  <li v-for="item in errorMessage">
                    {{ item }}
                  </li>
                </ul>
              </template>
            </ColoredBorderAlert>
          </template>
          <template v-if="editUserLoading">
            loading...
          </template>
          <template v-else-if="!editUserCompleted">
            <v-form v-model="validUserForm" @submit.prevent="handleEditAccountInformation">
              <v-text-field
                  v-model="username"
                  data-test="myProfileUsername"
                  label="Username"
                  :rules="requiredRule"
              ></v-text-field>
                <v-text-field
                    v-model="email"
                    label="Email"
                    data-test="myProfileEmail"
                    required
                    :rules="emailRules"
                    type="email"
                ></v-text-field>
              <div class="mt-5 mb-10">
                <Button
                    type="submit"
                    data-test="myProfileSaveChanges"
                    color="primary"
                    label="Save Changes"
                    :disabled="!validUserForm"
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
          </template>
          <template v-else>
            <p></p>
            <ColoredBorderAlert data-test="MyProfileChangeSuccess" type="info" icon="mdi-check">
              <template v-slot:content>
                Profile has been changed
              </template>
            </ColoredBorderAlert>
            <p data-test="changedUserName"><b>Username:</b> {{ username }}</p>
            <p data-test="changedEmail"><b>Email:</b> {{ email }}</p>
            <Button
                color="primary"
                outlined
                :click="clearEditUserStatus"
                label="Show Edit Form"
                :class="{
                  'width80 mx-auto d-block mb-2': $vuetify.breakpoint.xsOnly,
                  'mb-2': $vuetify.breakpoint.smAndUp
                }"
            />
          </template>

          <h2 class="title-size-2 mt-10">Change password</h2>
          <template v-if="changeError">
            <ColoredBorderAlert type="error" v-if="passwordErrorMessage">
              <template v-slot:content>
                <ul>
                  <li v-for="item in passwordErrorMessage">
                    {{ item }}
                  </li>
                </ul>
              </template>
            </ColoredBorderAlert>
          </template>
          <template v-if="changeLoading">
            loading...
          </template>
          <template v-else-if="!changeCompleted">
            <v-form v-model="validPasswordForm" ref="passwordForm" @submit.prevent="handleChangePassword">
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
                    label="Save Changes"
                    :disabled="!validPasswordForm"
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
          </template>
          <template v-else>
            <p></p>
            <ColoredBorderAlert type="info" icon="mdi-check">
              <template v-slot:content>
                Password has been changed
              </template>
            </ColoredBorderAlert>
            <Button
                color="primary"
                outlined
                :click="displayPasswordForm"
                label="Show Change Password Form"
                :class="{
                  'width80 mx-auto d-block mb-2': $vuetify.breakpoint.xsOnly,
                  'mb-2': $vuetify.breakpoint.smAndUp
                }"
            />
          </template>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import Button from "../components/DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../router/NETWORK_CONSTANTS";
import {mapState, mapActions} from "vuex";
import ColoredBorderAlert from "@/components/DynamicHelpResources/ColoredBorderAlert";

export default {
  name: "MyProfile",
  components: {Button, ColoredBorderAlert},
  computed: {
    ...mapState('auth', ['user', 'editUserCompleted', 'editUserLoading', 'editUserError']),
    ...mapState('password', ['changeCompleted', 'changeLoading', 'changeError'])
  },
  created: function () {
    this.username = this.user.username
    this.email = this.user.email
  },

  beforeRouteLeave(to, from, next) {
    this.clearEditUserStatus();
    this.clearPasswordStatus();
    next();
  },
  methods: {
    ...mapActions('auth', ['clearEditUserStatus']),
    ...mapActions('password', ['clearPasswordStatus']),
    displayPasswordForm() {
      this.password = ""
      this.newPassword = ""
      this.confirmNewPassword = ""
      this.clearPasswordStatus();
    },
    confirmNewPasswordRules() {
      return (
          this.newPassword === this.confirmNewPassword || `Passwords don't match`
      );
    },
    handleEditAccountInformation() {
      const payload = {newUsername: this.username, newEmail: this.email}
      this.$store.dispatch('auth/updateProfile', payload)
          .catch((error) => {
            let msg = []
            Object.keys(error).forEach(function (k) {
              // console.log(k + ' - ' + error[k]);
              msg.push('' + error[k])
            });
            this.errorMessage = msg
          })
    },
    handleChangePassword() {
      const payload = {
        oldPassword: this.password,
        password1: this.newPassword,
        password2: this.confirmNewPassword
      }
      this.$store.dispatch('password/changePassword', payload)
          .then(() => {
                this.$refs.passwordForm.reset()
              }
          ).catch((error) => {
        let msg = []
        Object.keys(error).forEach(function (k) {
          //  console.log(k + ' - ' + error[k]);
          msg.push('' + error[k])
        });
        this.passwordErrorMessage = msg
      })

    }
  },

  data: () => ({
    validPasswordForm: false,
    validUserForm: false,
    passwordSaved: false,
    showPassword: false,
    showNewPassword: false,
    showConfirmNewPassword: false,
    errorMessage: null,
    passwordErrorMessage: null,
    username: "",
    email: "",
    password: "",
    newPassword: "",
    confirmNewPassword: "",
    requiredRule: [value => !!value || "Required."],
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
