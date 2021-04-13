<template>
  <div class="mt-5 social-login-button pointer white--text" @click="handler">
    <div
        class="py-3 d-flex justify-center social-login-button__icon"
        :style="`backgroundColor: ${iconBgColor}`"
    >
      <v-icon color="white">{{ mdiIcon }}</v-icon>
    </div>
    <div
        class="py-3 d-flex justify-center social-login-button__label font-weight-bold"
        :style="`backgroundColor: ${labelBgColor}`"
    >
      {{ label }}
    </div>
  </div>
</template>

<style lang="scss" scoped>
.social-login-button {
  display: grid;
  grid-template-columns: 20% 80%;
}

.social-login-button__icon {
  border-top-left-radius: 8px;
  border-bottom-left-radius: 8px;
}

.social-login-button__label {
  border-top-right-radius: 8px;
  border-bottom-right-radius: 8px;
}
</style>

<script>
export default {
  name: "SocialLoginButton",
  props: ["handler", "mdiIcon", "iconBgColor", "label", "labelBgColor"]
};
</script>
