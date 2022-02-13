<template>
  <div id="password-reset-confirm-view">
    <h1>Reset Password Confirm</h1>
    <template v-if="resetLoading">
      loading...
    </template>
    <template v-else-if="!resetCompleted">
      <form @submit.prevent="submit">
        <input v-model="inputs.password1" type="password" id="password1" placeholder="password">
        <input v-model="inputs.password2" type="password" id="password2"
               placeholder="confirm password">
      </form>
      <button @click="submitPasswordReset(inputs)">
        Reset Password
      </button>
      <span class="error" v-show="resetError">
        A error occurred while processing your request:
           <ul>
                <li v-for="item in errorMessage">
                  {{ item }}
                </li>
              </ul>
      </span>
    </template>
    <template v-else>
      Your password has been reset.
      <router-link to="/log-in">return to login page</router-link>
    </template>
  </div>
</template>

<script>
import {mapActions, mapState} from 'vuex';

export default {
  data() {
    return {
      errorMessage: "",
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
    submitPasswordReset(inputs) {
      this.$store.dispatch('password/resetPassword', inputs)
          .then((resp) => {
          }).catch((error) => {
        console.log('error: ' + JSON.stringify(error))
        let msg = []
        Object.keys(error).forEach(function (k) {
          console.log(k + ' - ' + error[k]);
          msg.push(k + ' - ' + error[k][0])
        });
        this.errorMessage = msg
      })
    }
  }

};
</script>

<style>
form input {
  display: block
}
</style>
