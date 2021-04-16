<template>
  <div>
    <h1 class="title-size-1">Thank you for contacting us!</h1>
    <p class="mb-5">
      We received your email and will get back to you with a response as soon as
      possible.
    </p>
    <Button
        classes="mb-5"
        color="primary"
        :click="() => $router.push(NETWORK_CONSTANTS.HOME.PATH)"
        :class="{
        'width80 mx-auto d-block mb-5': $vuetify.breakpoint.xsOnly
      }"
        label="Go to Home"
    />
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
import Button from "../DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../../router/NETWORK_CONSTANTS";

export default {
  components: {Button},
  name: "ContactUsSubmitted",
  data: () => ({NETWORK_CONSTANTS})
};
</script>
