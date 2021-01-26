<template>


   <v-card width="400" class="mx-auto mt-5">
    <v-card-title>
      <h1 class="display-1">Reset Password</h1>
    </v-card-title>
    <v-card-text>
     <template v-if="!emailCompleted">
      <v-form @submit.prevent="submit">
        <v-text-field v-model="inputs.email" id="email" placeholder="email"></v-text-field>
      </v-form>
      </template>
       <template v-else>
      <div>
        Check your inbox for a link to reset your password. If an email doesn't appear within a few
        minutes, check your spam folder.
      </div>
      </template>
      <v-divider></v-divider>
      <v-card-actions>

     <template v-if="!emailCompleted">
          <v-btn @click="sendPasswordResetEmail(inputs)">
        send email
      </v-btn>
      </template>
      <template v-else>
       <router-link to="/login">
        return to login page
      </router-link>
      </template>
      </v-card-actions>
    </v-card-text>
  </v-card>
</template>

<script>
import { mapActions, mapState } from 'vuex';

export default {
  data() {
    return { inputs: { email: '' } };
  },
  computed: mapState('password', [
    'emailCompleted',
    'emailError',
    'emailLoading',
  ]),
  methods: mapActions('password', [
    'sendPasswordResetEmail',
    'clearEmailStatus',
  ]),
  beforeRouteLeave(to, from, next) {
    this.clearEmailStatus();
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
