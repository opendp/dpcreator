<template>
  <div
      class="d-flex justify-center"
      :class="{ 'flex-column align-center py-5': $vuetify.breakpoint.xsOnly }"
  >
    <Button v-if="!isAuthenticated"
            data-test="loginButton"
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
    <Button v-if="!isAuthenticated"
            data-test="createAccountButton"
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
    <Button v-if="isAuthenticated"
            data-test="accountContinueButton"
            classes="account-buttons__item"
            :class="{
        'mx-5 my-2 width80': $vuetify.breakpoint.xsOnly,
        'ma-2': $vuetify.breakpoint.smAndUp
      }"
            color="primary"
            outlined
            :click="continueAction"
            :disabled="buttonsDisabled"
            label="Continue"
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
import {mapGetters, mapState} from "vuex";

export default {
  components: {Button},
  name: "AccountButtonsBar",
  computed: {
    ...mapGetters('auth', ['isAuthenticated']),
    ...mapState('dataverse', ['handoffId']),
    ...mapState('auth', ['user']),
  },
  methods: {
    continueAction() {
      console.log('continue')
      if (this.handoffId) {
        console.log('handoff' + JSON.stringify(this.user))
        const payload = {
          handoffId: this.handoffId,
          OpenDPUserId: this.user.objectId
        }
        this.$store.dispatch('dataverse/doHandoff', payload)
            .then(() => {
              this.$router.push(NETWORK_CONSTANTS.WELCOME.PATH)
            })
      } else {
        this.$router.push(NETWORK_CONSTANTS.MY_DATA.PATH)
      }
    }
  },
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
