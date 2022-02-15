<template>
  <div class="my-profile mt-5">
    <EditSuccessAlert :successFlag="saved" text="Changes saved"/>
    {{ this.$route.query['saved'] }}
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
          <template v-if="editUserLoading">
            loading...
          </template>
          <template v-else-if="editUserError">
            Error editing user
          </template>
          <template v-else-if="!editUserCompleted">

            <v-form @submit.prevent="handleEditAccountInformation">
              <v-text-field
                  v-model="username"
                  data-test="myProfileUsername"
                  label="Username"
                  required
              ></v-text-field>
              <!-- For now, don't allow editing of the email, because it would require a new endpoint
              and another email verification
              <v-text-field
                  v-model="email"
                  label="Email"
                  required
                  :rules="emailRules"
                  type="email"
              ></v-text-field> -->
              <div class="mt-5 mb-10">
                {{ email }}
              </div>
              <div class="mt-5 mb-10">
                <Button
                    type="submit"
                    color="primary"
                    label="Save Changes"
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
            <ColoredBorderAlert type="info" icon="mdi-check">
              <template v-slot:content>
                Username has been changed
              </template>
            </ColoredBorderAlert>
            <p><b>Username:</b> {{ username }}</p>
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
          <ColoredBorderAlert type="error" v-if="errorMessage">
            <template v-slot:content>
              Form Error:
              <ul>
                <li v-for="item in errorMessage">
                  {{ item }}
                </li>
              </ul>
            </template>
          </ColoredBorderAlert>
          <EditSuccessAlert :successFlag="passwordSaved" text="New password saved"/>


          <v-form ref="passwordForm" @submit.prevent="handleChangePassword">
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
import {mapState, mapActions} from "vuex";
import auth from '../api/auth';
import ColoredBorderAlert from "@/components/DynamicHelpResources/ColoredBorderAlert";
import EditSuccessAlert from "@/components/DynamicHelpResources/EditSuccessAlert";
export default {
  name: "MyProfile",
  components: {Button, EventSuccessAlert, EditSuccessAlert, ColoredBorderAlert},
  computed: {
    ...mapState('auth', ['user', 'editUserCompleted', 'editUserLoading', 'editUserError']),

  },
  created: function () {
    this.username = this.user.username
    this.email = this.user.email
  },
  beforeRouteLeave(to, from, next) {
    this.clearEditUserStatus();
    next();
  },
  methods: {
    ...mapActions('auth', ['clearEditUserStatus']),
    confirmNewPasswordRules() {
      return (
          this.newPassword === this.confirmNewPassword || `Passwords don't match`
      );
    },
    handleEditAccountInformation() {
      this.$store.dispatch('auth/changeUsername', this.username)
    },
    handleChangePassword() {
      auth.changePassword(this.password, this.newPassword, this.confirmNewPassword)
          .then(() => {
                this.$refs.passwordForm.reset()
                this.passwordSaved = true
              }
          ).catch((error) => {
        let msg = []
        Object.keys(error).forEach(function (k) {
          console.log(k + ' - ' + error[k]);
          msg.push(k + ' - ' + error[k])
        });
        this.errorMessage = msg
      })

    }
  },

  data: () => ({
    saved: false,
    passwordSaved: false,
    showPassword: false,
    showNewPassword: false,
    showConfirmNewPassword: false,
    errorMessage: null,
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
