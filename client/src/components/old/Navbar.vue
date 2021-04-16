<template>
  <!--
   <v-app-bar app color="primary" dark>
      <v-toolbar-title>Vuetify Dashboard</v-toolbar-title>
      <v-spacer></v-spacer>
     <v-btn :key="Home-header-link" text rounded @click="$router.push('home')" >Home</v-btn>
     <template v-if="isAuthenticated">
      <v-btn :key="Logout-header-link" text rounded @click="$router.push('logout')" >Logout</v-btn>
       <v-btn :key="PasswordReset-header-link" text rounded @click="$router.push('password_reset')" >Reset Password</v-btn>
     </template>
     <template v-if="!isAuthenticated">
       <v-btn :key="Login-header-link" text rounded @click="$router.push('login')" >Login</v-btn>
     </template>

      v-btn @click="toggleTheme" text rounded>
        Toggle Theme
      </v-btn

    </v-app-bar>
    -->
<ul class="navbar" id="navbar">
    <li>
      <router-link to="/logout">logout {{ username }}</router-link>
    </li>
    <li><router-link to="/about">about</router-link></li>
    <li><router-link to="/password_reset">reset password</router-link></li>
  </ul>
</template>

<script>

import auth from '../../api/auth'
import {
  mapActions,
  mapGetters,
  mapState,
} from 'vuex';

export default {
  name: 'navbar',
  created() {
    this.$store.dispatch('auth/fetchUser')
  },
  computed: {
    ...mapGetters('auth', ['isAuthenticated']),
    ...mapState('auth', ['user']),
    username() {
      return (this.user) ? this.user.username : null
    }
  },
}
</script>


<style scoped>
ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

li {
  display: inline;
  float: right;
}

a {
  color: #1a1a1a;
  display: inline-block;
  text-align: center;
  padding: 6px 12px;
  text-decoration: none;
  font-size: 14px;
}

a:hover {
  color: #cc0000;
  text-decoration: none;
}
</style>
