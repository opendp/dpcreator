<template>
  <v-footer color="grey lighten-3 py-5" padless>
    <v-container :class="{ 'px-11': $vuetify.breakpoint.smAndDown }">
      <v-row justify="center" no-gutters>
        <v-col class="py-5 logo" cols="12" md="3">
          <router-link class="router-link" to="/">Logo</router-link>
        </v-col>
        <v-col class="py-5" cols="12" md="9">
          <router-link
              to="/contact-us"
              class="d-block text-decoration-none footer-links"
          >Contact us
          </router-link
          >
          <router-link
              to="/terms-and-conditions"
              class="d-block text-decoration-none footer-links"
          >Terms & Conditions
          </router-link
          >
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<style lang="scss" scoped>
.footer-links {
  font-weight: 600;
  font-size: 1.25rem;
  margin-bottom: 1rem;
}
</style>

<script>
export default {
  name: "Footer"
};
</script>
