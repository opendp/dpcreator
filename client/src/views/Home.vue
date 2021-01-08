<template>
  <div id="home-view">
    <h1>Home</h1>
      <h3 v-if="isAuthenticated">hello, {{user}}</h3>
      <h3 v-if="!isAuthenticated">not authenticated</h3>
    </div>
</template>

<script>
import auth from '../api/auth'
import {
  mapActions,
  mapGetters,
  mapState,
} from 'vuex';

export default {
  name: 'home',
  created() {
      this.$store.dispatch('auth/fetchUser')
  },
  computed: {
    ...mapGetters('auth', ['isAuthenticated']),
    ...mapState('auth', ['user']),
  },
   methods: {
    onGoogleSignInSuccess(resp) {
      console.log('success!')
      console.log(resp)
      console.log(resp.xc)
      const access_token = resp.xc.access_token
      console.log(access_token)
      console.log('variable type: ' + typeof (access_token))
      this.$store.dispatch('auth/googleLogin', access_token).then(() => this.$router.push('/'))
      .then(() => auth.getAccountDetails().then(({data}) => console.log(data) ))
        //  then((resp) => this.user = resp.data.user)
    },
    onGoogleSignInError (error) {
      console.log('OH NOES', error)
    },
    isEmpty (obj) {
      return Object.keys(obj).length === 0
    }
  },
}

</script>
