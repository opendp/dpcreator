<template>
  <section>
    <div
        id="account-buttons--fixed"
        class="account-buttons elevation-5 white"
        v-bind:class="buttonsShouldStick ? 'account-buttons--fixed' : 'd-none'"
    >
      <AccountButtonsBar/>
    </div>
    <div id="account-buttons--dummy" class="account-buttons white">
      <AccountButtonsBar/>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.account-buttons--fixed {
  position: fixed;
  bottom: 0;
  width: 100%;
  z-index: 1;
}
</style>

<script>
import AccountButtonsBar from "./AccountButtonsBar.vue";

export default {
  name: "AccountButtons",
  components: {AccountButtonsBar},
  data: function () {
    return {
      buttonsShouldStick: true
    };
  },
  mounted() {
    const that = this;
    this.$root.$on("buttonsShouldNotStick", function () {
      that.buttonsShouldStick = false;
    });
    this.$root.$on("buttonsShouldStick", function () {
      that.buttonsShouldStick = true;
    });
  }
};
</script>
