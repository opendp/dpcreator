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
    <button @click="googleLogin({})" id="google-login-button">
      login with Google
    </button>
      <g-signin-button
            v-if="isEmpty(user)"
            :params="googleSignInParams"
            @success="onGoogleSignInSuccess"
            @error="onGoogleSignInError"
          >
            <button class="btn btn-block btn-success">
              Vue Component Google Signin
            </button>
          </g-signin-button>
    <div>
       <a href="/account/google/login">Login with Google direct link</a> |

       <router-link to="/register">create account</router-link> |
      <router-link to="/password_reset">reset password</router-link>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      user: {},
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
    googleLogin({}) {
      this.$store.dispatch('auth/googleLogin',{})
          .then(() => this.$router.push('/'));
    },
     onGoogleSignInSuccess (resp) {
      console.log('success!')
      console.log(resp)
      const token = resp.xc.access_token
      axios.post('http://localhost:8000/rest-auth/google/', {
        access_token: token
      })
        .then(resp => {
          console.log(resp)
          this.user = resp.data.key
        })
        .catch(err => {
          console.log(err.response)
        })
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
