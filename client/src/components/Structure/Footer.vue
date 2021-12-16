<template>
  <v-footer color="footer" class="py-5" padless>
    <v-container :class="{ 'px-11': $vuetify.breakpoint.smAndDown }">
      <v-row justify="center" no-gutters>

        <v-col class="pt-5 pb-10" cols="12" md="10">
          <a
              class="font-weight-bold text-decoration-none"
              href="mailto:info@opendp.org"
          >Contact us</a
          >
          <router-link
              :to="NETWORK_CONSTANTS.TERMS_AND_CONDITIONS.PATH"
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
import NETWORK_CONSTANTS from "../../router/NETWORK_CONSTANTS";
export default {
  name: "Footer",
  data: () => ({
    NETWORK_CONSTANTS
  })
};
</script>
