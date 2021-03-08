<template>
  <v-card width="400" class="mx-auto mt-5">
    <v-card-title>
      <h1 class="display-1">Login</h1>
    </v-card-title>
    <v-card-text>
      <v-form @submit.prevent="submit" v-model="formValidity">
        <v-text-field required label="Username" v-model="inputs.username" prepend-icon="mdi-account-circle"/>
        <v-text-field
            :type="showPassword ? 'text' : 'password'"
            label="Password"
            v-model="inputs.password"
            prepend-icon="mdi-lock"
            :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
            @click:append="showPassword = !showPassword"
        />
        <v-alert dense outlined type="error" v-show="error">
          An error occurred while processing your request.
          <ul>
            <li v-for="err in loginErrors">{{ err }}</li>
          </ul>
        </v-alert>
      </v-form>
      <v-divider></v-divider>
      <v-card-actions>
        <v-btn @click="$router.push('register')" color="success">Register</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="info" @click="login(inputs)">Login</v-btn>
        <v-spacer></v-spacer>
        <g-signin-button
            :params="googleSignInParams"
            @success="onGoogleSignInSuccess"
            @error="onGoogleSignInError"
        >
          <v-btn color="info">
            Google Signin
          </v-btn>
        </g-signin-button>
      </v-card-actions>
    </v-card-text>
  </v-card>
</template>

<script>
import auth from '../api/auth'
import {  mapState } from 'vuex';

export default {
  data() {
    return {
      formValidity: false,
      showPassword: false,
      errorMessage: null,
      googleSignInParams: {
        client_id: '725082195083-1srivl3ra9mpc1q5ogi7aur17vkjuabg.apps.googleusercontent.com',
      },
      inputs: {
        username: '',
        password: '',
      },
    };
  },
  computed: {
    ...mapState('auth', ['error', 'user']),
    ...mapState('dataverse', ['dvParams']),
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
    login({username, password}) {
      this.errorMessage = null;
      this.$store.dispatch('auth/login', {username, password})
          .catch((data) => {
            this.errorMessage = data;
          })
          .then(() => {
            if (!this.error) {
              this.checkDataverseUser();
              this.$router.push('/');
            }
          })
          .catch((data) => {
            console.log(data);
            this.errorMessage = data
          });
    },
    onGoogleSignInSuccess(resp) {
      const access_token = resp.getAuthResponse(true).access_token
      this.$store.dispatch('auth/googleLogin', access_token)
          .then(() => {
            this.checkDataverseUser();
            this.$router.push('/')
          })
    },
    onGoogleSignInError(error) {
      console.log('OH NOES', error)
    },
    isEmpty(obj) {
      return Object.keys(obj).length === 0
    },
    checkDataverseUser() {
        this.$store.dispatch('auth/fetchUser')
            .then(() => {
              // TODO: replace pk with UUID
              this.$store.dispatch('update/updateDataverseUser', this.user['pk'])
                  .catch(({data}) => console.log("error: " + data))
            })
    }
  },
};
</script>

<style>
form input {
  display: block
}
</style>
