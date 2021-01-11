<template>
  <div id="app">
   <router-link to="/">Home</router-link> |
    <template v-if="!isAuthenticated">
      <router-link to="/login">Login</router-link>
    </template>
    <navbar v-if="isAuthenticated"></navbar>
    <router-view/>
  </div>
  </template>


<script>
import { mapGetters } from 'vuex';

import Navbar from './components/Navbar';

export default {
  name: 'app',
  components: {
    Navbar,
  },
  computed: mapGetters('auth', [
    'isAuthenticated',
  ]),
};
</script>
<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
