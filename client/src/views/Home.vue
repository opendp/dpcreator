<template>
  <div id="home-view">
    <h1>Home</h1>
      <h3 v-if="isAuthenticated">hello, {{user}}</h3>
      <h3 v-if="!isAuthenticated">not authenticated</h3>
    </div>
</template>

<script>
import auth from '../api/auth'
import dataverse from '../api/dataverse'
import {
  mapActions,
  mapGetters,
  mapState,
} from 'vuex';

export default {
  name: 'home',
  created() {
    const apiGeneralToken = this.$route.query.apiGeneralToken
    const siteUrl = this.$route.query.siteUrl
    const fileId = this.$route.query.fileId
    const filePid = this.$route.query.filePid
    const datasetPid = this.$route.query.datasetPid
    if (apiGeneralToken && siteUrl) {
      dataverse.getUserInfo(apiGeneralToken, siteUrl).then((data) => console.log(data))
      if (datasetPid && (fileId || filePid)) {
        dataverse.getDatasetInfo(apiGeneralToken, siteUrl, datasetPid, fileId, filePid).then((data) => console.log(data));
      }
    }

  },
  computed: {
    ...mapGetters('auth', ['isAuthenticated']),
    ...mapState('auth', ['user']),
  },
   methods: {
    onGoogleSignInSuccess(resp) {
      console.log('success!')
      const access_token = resp.xc.access_token
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
