<template>
  <div>
    <h1 class="title-size-1">Thank you for contacting us!</h1>
    <p class="mb-5">
      We received your email and will get back to you with a response as soon as
      possible.
    </p>
    <v-btn class="mb-5" color="primary" @click="$router.push('/')"
    >Go to home
    </v-btn
    >
  </div>
</template>

<style lang="scss" scoped>
p {
  @media (min-width: 601px) {
    max-width: 50%;
  }
  @media (min-width: 961px) {
    max-width: 35%;
  }
}
</style>

<script>
export default {
  name: "ContactUsSubmitted"
};
</script>
