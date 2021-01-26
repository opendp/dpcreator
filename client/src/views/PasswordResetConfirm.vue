<template>
  <v-card width="400" class="mx-auto mt-5">
    <v-card-title>
      <h1 class="display-1">Reset Password Confirm</h1>
    </v-card-title>
    <v-card-text>
      <template v-if="resetLoading">
        loading...
      </template>
      <template v-else-if="!resetCompleted">
        <v-form @submit.prevent="submit">
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
        </v-form>
      </template>
      <template v-else>
        Your password has been reset.
      </template>
    </v-card-text>
    <v-card-actions>
      <template v-if="!resetCompleted">
        <v-btn color="info" @click="resetPassword(inputs)">
          Reset Password
        </v-btn>
      </template>
      <template v-else>
        <router-link to="/login">return to login page</router-link>
      </template>
    </v-card-actions>
  </v-card>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
  data() {
    return {
      showPassword: false,
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
  methods: mapActions('password', [
    'resetPassword',
    'clearResetStatus',
  ]),
};
</script>

<style>
form input {
  display: block
}
</style>
