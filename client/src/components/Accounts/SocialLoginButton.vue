<template>
  <g-signin-button
      :params="googleSignInParams"
      @success="onGoogleSignInSuccess"
      @error="onGoogleSignInError"
  >
    <div
        class="mt-5 social-login-button pointer white--text"
        :class="{
      'width80 mx-auto': $vuetify.breakpoint.xsOnly
    }"
    >
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
  </g-signin-button>
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
  props: ["handler", "mdiIcon", "iconBgColor", "label", "labelBgColor"],

  methods: {
    onGoogleSignInSuccess(resp) {
      const access_token = resp.getAuthResponse(true).access_token
      this.handler(access_token)

    },
    onGoogleSignInError(error) {
      console.log('google signin error:', error)
    },
    isEmpty(obj) {
      return Object.keys(obj).length === 0
    },

  },
  data: () => ({
    googleSignInParams: {
      client_id: '725082195083-1srivl3ra9mpc1q5ogi7aur17vkjuabg.apps.googleusercontent.com',
    }
  })
}

</script>
