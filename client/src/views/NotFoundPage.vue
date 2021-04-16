<template>
  <div class="not-found-page d-flex flex-column align-center mt-10">
    <p class="subtitle">404 Error</p>
    <h2 class="title-size-1 mb-0">Sorry, this page isn't available.</h2>
    <p class="my-10">
      <router-link
          :to="NETWORK_CONSTANTS.CONTACT_US.PATH"
          class="text-decoration-none primary--text"
      >
        Get in touch
      </router-link>
      with the site owners for more information.
    </p>
    <Button
        color="primary"
        :click="() => $router.push(NETWORK_CONSTANTS.HOME.PATH)"
        label="Go to Home"
    />
  </div>
</template>

<style lang="scss" scoped>
.subtitle {
  font-size: 25px;
  font-weight: lighter;
}
</style>

<script>
import Button from "../components/DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../router/NETWORK_CONSTANTS";

export default {
  components: {Button},
  name: "NotFoundPage",
  data: () => ({
    NETWORK_CONSTANTS
  })
};
</script>
