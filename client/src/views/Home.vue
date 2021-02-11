<template>
  <div id="home-view">
    <h1>Home</h1>
    <!--
     remove this for now, because we may not want to get show info from dataverse before OpenDP user logs in
      <h3 v-if="dvUser">Welcome, {{dvUser['displayName']}}<
      /h3>

       <p v-if="dvDataset">You have been directed to OpenDP by the Dataverse Installation at {{siteUrl}}
       to create differentially private statistics for the dataset {{datasetPid}}</p>
      <p >Here is some explanatory text, describing differential privacy and OpenDP,
      so that you will understand what the app does.</p>
      -->
    <template v-if="!isAuthenticated">
      <p>If you have been here before, please login: </p>
      <v-btn to="/login">Login</v-btn>
      <br/>
      <p>Here is some help text info we want the user to view before allowing them to create an account.
        It can be replaced by a TreeView component, and we can enable the Create Account button after
        the user has opened and read through all the tips in the TreeView. Here we have a checkbox that
        the user must check to confirm that they understand the tips/instructions,
        before enabling Create Account button.</p>
      <v-checkbox
          v-model="tipsCheckbox"
          :label="`I understand the tips.`"
      ></v-checkbox>
      <v-btn :disabled="!tipsCheckbox" to="/Register">Create Account</v-btn>
    </template>

    <template v-if="isAuthenticated && !isTermsAccepted">
      Here are the OpenDP terms of Service text that you must agree with.
      <v-btn @click="acceptTerms">Accept</v-btn>
    </template>
    <template v-if="isAuthenticated && isTermsAccepted">
      Click here to begin/continue the process of generating a DP Release for your Data
      <v-btn to="/VariableInfo">Get Started</v-btn>
    </template>
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
    this.siteUrl = this.$route.query.siteUrl
    const fileId = this.$route.query.fileId
    const filePid = this.$route.query.filePid
    this.datasetPid = this.$route.query.datasetPid
    if (apiGeneralToken && this.siteUrl) {
      dataverse.getUserInfo(apiGeneralToken, this.siteUrl).then((data) => {
        this.dvUser = data['data']['data'];
        console.log(data['data']['data']);
        console.log(this.dvUser['displayName'])
      })
      if (this.datasetPid && (fileId || filePid)) {
        dataverse.getDatasetInfo(apiGeneralToken, this.siteUrl, this.datasetPid, fileId, filePid)
            .then((data) => {
              this.dvDataset = data;
              console.log(data)
            });
      }
    }

  },
  data() {
    return {
      tipsCheckbox: false,
      dvUser: null,
      dvDataset: null,
      siteUrl: null,
      datasetPid: null
    };
  },
  computed: {
    ...mapGetters('auth', ['isAuthenticated', 'isTermsAccepted']),
    ...mapState('auth', ['user']),
  },
  methods: {
    onGoogleSignInSuccess(resp) {
      console.log('success!')
      const access_token = resp.xc.access_token
      this.$store.dispatch('auth/googleLogin', access_token).then(() => this.$router.push('/'))
          .then(() => auth.getAccountDetails().then(({data}) => console.log(data)))
      //  then((resp) => this.user = resp.data.user)
    },
    onGoogleSignInError(error) {
      console.log('OH NOES', error)
    },
    acceptTerms() {
      this.acceptedTerms = true
      this.$store.dispatch('auth/setTermsAccepted', true)
    },
    isEmpty(obj) {
      return Object.keys(obj).length === 0
    }
  },
}

</script>
