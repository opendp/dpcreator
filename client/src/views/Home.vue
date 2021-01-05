<template>
  <div id="home-view">
    <h1>Home</h1>
      <h3 v-if="isAuthenticated">authenticated!</h3>

    </div>
</template>

<script>

import {
  mapActions,
  mapGetters,
  mapState,
} from 'vuex';

export default {
  name: 'home',

  computed: {
    ...mapGetters('auth', ['isAuthenticated']),
  },
}

</script>
