<template>
  <div class="not-found-page d-flex flex-column align-center mt-16">
    <p class="subtitle">404 Error</p>
    <h2 class="title-size-1 mb-0">Sorry, this page isn't available.</h2>
    <p class="my-10">
      <router-link to="/contact-us" class="text-decoration-none primary--text">
        Get in touch
      </router-link>
      with the site owners for more information.
    </p>
    <v-btn color="primary" @click="$router.push('/')">Go to Home</v-btn>
  </div>
</template>

<style lang="scss" scoped>
.subtitle {
  font-size: 25px;
  font-weight: lighter;
}
</style>

<script>
export default {
  name: "404"
};
</script>
