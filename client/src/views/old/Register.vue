<template>
  <v-card width="400" class="mx-auto mt-5">
    <v-card-title>
      <h1 class="display-1">Register</h1>
    </v-card-title>
    <v-card-text>
      <template v-if="registrationLoading">
        loading...
      </template>
      <template v-else-if="!registrationCompleted">
        <v-form @submit.prevent="submit" v-model="formValidity">
          <v-text-field
              v-model="inputs.username"
              label="Username"
              :rules="[v => !!v || 'Username is required']"
          />
          <v-text-field
              :type="showPassword ? 'text' : 'password'"
              label="Password"
              v-model="inputs.password1"
              prepend-icon="mdi-lock"
              :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append="showPassword = !showPassword"
              :rules="passwordRules"
          />
          <v-text-field
              :type="showPassword ? 'text' : 'password'"
              label="Confirm Password"
              v-model="inputs.password2"
              prepend-icon="mdi-lock"
              :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append="showPassword = !showPassword"
              :rules="passwordRules"
          />
          <v-text-field v-model="inputs.email" :rules="emailRules" type="email" id="email" label="Email"/>
          <v-alert dense outlined type="error" v-show="registrationError">
            An error occurred while processing your request.
            <ul>
              <li v-for="err in registrationErrors">{{ err }}</li>
            </ul>
          </v-alert>
        </v-form>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="info" :disabled="!formValidity" @click="submitRegister()">
            Create Account
          </v-btn>
          <v-spacer></v-spacer>
          <g-signin-button
              :params="googleSignInParams"
              @success="onGoogleSignInSuccess"
              @error="onGoogleSignInError"
          >
            <v-spacer></v-spacer>
            <v-btn color="info">
              Sign In with Google
            </v-btn>
          </g-signin-button>
        </v-card-actions>
        Already have an account?
        <router-link to="/login">login</router-link>
        |
        <router-link to="/password_reset">reset password</router-link>

      </template>
      <template v-else>
        <div>
          Registration complete. You should receive an email shortly with instructions on how to
          activate your account.
        </div>
        <div>
          <router-link to="/login">return to login page</router-link>
        </div>
      </template>
    </v-card-text>
  </v-card>
</template>

<script>
import {mapActions, mapState, mapGetters} from 'vuex';

export default {
  data() {
    return {
      showPassword: false,
      errorMessage: null,
      formValidity: false,
      googleSignInParams: {
        // TODO:get from a shared location, instead of hard-coded
        client_id: '725082195083-1srivl3ra9mpc1q5ogi7aur17vkjuabg.apps.googleusercontent.com',
      },
      inputs: {
        username: '',
        password1: '',
        password2: '',
        email: '',
      },
      emailRules: [
        value => value.indexOf('@') !== 0 || 'Email should have a username.',
        value => value.includes('@') || 'Email should include an @ symbol.',
        value => value.includes('.') || 'Email should include a period symbol.',
        value =>
            value.indexOf('.') <= value.length - 3 ||
            'Email should contain a valid domain extension.'
      ],
      passwordRules: [
        v => !!v || 'Password is required',
        v => (v && v.length >= 9) || 'Password must have 9+ characters',]
    };
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

  methods: {
    ...mapActions('signup', [
      'createAccount',
      'clearRegistrationStatus',
    ], 'auth', ['fetchUser']),
    submitRegister() {
      this.$store.dispatch('signup/createAccount', this.inputs)
          .then((resp) => {
                if (this.handoffId) {
                  const openDPUserId = resp.data[0]
                  this.$store.dispatch('dataverse/updateDataverseUser',
                      openDPUserId)
                }
              }
          )
    },
    onGoogleSignInError(error) {
      console.log('Google sign in error: ', error)
    },
    onGoogleSignInSuccess(resp) {
      const access_token = resp.getAuthResponse(true).access_token
      this.$store.dispatch('auth/googleLogin', access_token)
          .then(() => {
            this.$store.dispatch('auth/fetchUser')
                .then(() => {
                  if (this.handoffId) {
                    this.$store.dispatch('dataverse/updateDataverseUser',
                        this.user['object_id'])
                  }
                })
          })
          .then(() => this.$router.push('/old'))
    },

    beforeRouteLeave(to, from, next) {
      this.clearRegistrationStatus();
      next();
    },
  }
}
</script>
