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
        <v-form @submit.prevent="submit">
          <v-text-field v-model="inputs.username" label="Username"/>
          <v-text-field
              :type="showPassword ? 'text' : 'password'"
              label="Password"
              v-model="inputs.password1"
              prepend-icon="mdi-lock"
              :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append="showPassword = !showPassword"
          />
          <v-text-field
              :type="showPassword ? 'text' : 'password'"
              label="Confirm Password"
              v-model="inputs.password2"
              prepend-icon="mdi-lock"
              :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
              @click:append="showPassword = !showPassword"
          />
          <v-text-field v-model="inputs.email" type="email" id="email" label="Email"/>
          <v-alert dense outlined type="error" v-show="registrationError">
            An error occured while processing your request.
            <ul>
              <li v-for="err in registrationErrors">{{ err }}</li>
            </ul>
          </v-alert>
        </v-form>
        <v-divider></v-divider>
        <v-card-actions>
          <v-btn color="info" @click="createAccount(inputs)">
            Create Account
          </v-btn>
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
import { mapActions, mapState,mapGetters } from 'vuex';

export default {
  data() {
    return {
      showPassword: false,
      inputs: {
        username: '',
        password1: '',
        password2: '',
        email: '',
      },
    };
  },
  computed: {
    ...mapState('signup', ['registrationCompleted',
      'registrationError',
      'registrationLoading',
      'errorMessage']),
    registrationErrors() {

      if (this.errorMessage != null) {
        if (this.errorMessage['password1'] != null) {
          return this.errorMessage['password1']
        } else if (this.errorMessage['email'] != null) {
          return this.errorMessage['email'];
        } else if (this.errorMessage['non_field_errors'] != null) {
          return this.errorMessage['non_field_errors'];
        }
      }
      return this.errorMessage;
    }
  },

  methods: mapActions('signup', [
    'createAccount',
    'clearRegistrationStatus',
  ]),
  beforeRouteLeave(to, from, next) {
    this.clearRegistrationStatus();
    next();
  },
};
</script>

<style>
form input {
  display: block
}

.error {
  color: crimson;
  font-size: 12px;
}
</style>
