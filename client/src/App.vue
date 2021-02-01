<template>
  <div id="app">
    <v-app>
        <router-link to="/">Home</router-link>
        |
        <template v-if="!isAuthenticated">
          <router-link to="/login">Login</router-link>
        </template>
        <navbar v-if="isAuthenticated"></navbar>
        <v-content>

        <router-view/>
      </v-content>
    </v-app>
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
