<template>
  <div id="login-view">
    <h1>Login</h1>
    <form @submit.prevent="submit">
      <input v-model="inputs.username" type="text" id="username" placeholder="username">
      <input v-model="inputs.password" type="password" id="password" placeholder="password">
    </form>
    <button @click="login(inputs)" id="login-button">
      login
    </button>

      <g-signin-button
            :params="googleSignInParams"
            @success="onGoogleSignInSuccess"
            @error="onGoogleSignInError"
          >
            <button style="width:auto" class="btn btn-block btn-success">

              Vue Component Google Signin
            </button>
          </g-signin-button>
    <div>

       <router-link to="/register">create account</router-link> |
      <router-link to="/password_reset">reset password</router-link>
    </div>
  </div>
</template>

<script>
import auth from '../api/auth'
export default {
  data() {
    return {
      googleSignInParams: {
        client_id: '725082195083-1srivl3ra9mpc1q5ogi7aur17vkjuabg.apps.googleusercontent.com',
      },
      inputs: {
        username: '',
        password: '',
      },
    };
  },
  methods: {
    login({ username, password }) {
      this.$store.dispatch('auth/login', { username, password })
        .then(() => this.$router.push('/'));
    },
    onGoogleSignInSuccess(resp) {
      const access_token = resp.Bc.access_token
      this.$store.dispatch('auth/googleLogin', access_token).then(() => this.$router.push('/'))
      .then(() => auth.getAccountDetails().then(({data}) => console.log(data) ))

    },
    onGoogleSignInError (error) {
      console.log('OH NOES', error)
    },
    isEmpty (obj) {
      return Object.keys(obj).length === 0
    }
  },
};
</script>

<style>
form input {
  display: block
}
</style>
