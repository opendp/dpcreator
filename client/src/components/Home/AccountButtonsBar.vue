<template>
  <div class="d-flex justify-center">
    <v-btn
        class="ma-5 account-buttons__item"
        color="primary"
        @click="$router.push('/log-in')"
        :disabled="buttonsDisabled"
    >Log in
    </v-btn
    >
    <v-btn
        class="ma-5 account-buttons__item"
        color="primary"
        outlined
        @click="$router.push('/sign-up')"
        :disabled="buttonsDisabled"
    >Create account
    </v-btn
    >
  </div>
</template>

<style lang="scss" scoped>
.account-buttons__item {
  transition: color 1s, background-color 1s;
}
</style>

<script>
export default {
  name: "AccountButtonsBar",
  data: () => ({
    buttonsDisabled: true
  }),
  mounted() {
    const that = this;
    this.$root.$on("termsOfServiceCheckboxChanged", function (checkboxStatus) {
      that.buttonsDisabled = !checkboxStatus;
    });
  }
};
</script>
