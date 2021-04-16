<template>
  <div
      class="d-flex justify-center"
      :class="{ 'flex-column align-center py-5': $vuetify.breakpoint.xsOnly }"
  >
    <Button
        classes="account-buttons__item"
        :class="{
        'mx-5 my-2 width80': $vuetify.breakpoint.xsOnly,
        'ma-2': $vuetify.breakpoint.smAndUp
      }"
        color="primary"
        :click="() => $router.push(NETWORK_CONSTANTS.LOGIN.PATH)"
        :disabled="buttonsDisabled"
        label="Log in"
    />
    <Button
        classes="account-buttons__item"
        :class="{
        'mx-5 my-2 width80': $vuetify.breakpoint.xsOnly,
        'ma-2': $vuetify.breakpoint.smAndUp
      }"
        color="primary"
        outlined
        :click="() => $router.push(NETWORK_CONSTANTS.SIGN_UP.PATH)"
        :disabled="buttonsDisabled"
        label="Create account"
    />
  </div>
</template>

<style lang="scss" scoped>
.account-buttons__item {
  transition: color 1s, background-color 1s;
}
</style>

<script>
import Button from "../DesignSystem/Button.vue";
import NETWORK_CONSTANTS from "../../router/NETWORK_CONSTANTS";

export default {
  components: {Button},
  name: "AccountButtonsBar",
  data: () => ({
    buttonsDisabled: true,
    NETWORK_CONSTANTS
  }),
  mounted() {
    const that = this;
    this.$root.$on("termsOfServiceCheckboxChanged", function (checkboxStatus) {
      that.buttonsDisabled = !checkboxStatus;
    });
  }
};
</script>
