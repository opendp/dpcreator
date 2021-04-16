<template>
  <v-container class="alert-wrapper event-success-alert">
    <v-alert
        v-model="showAlert"
        icon="mdi-check"
        transition="scale-transition"
        class="alert soft_primary px-10"
    >
      {{ text }}
    </v-alert>
  </v-container>
</template>

<style lang="scss">
.event-success-alert {
  &.alert-wrapper {
    position: relative;
  }

  .alert {
    position: absolute !important;
    top: 0;
    right: 0;
    z-index: 1;
    @media (max-width: 600px) {
      text-align: center;
      width: 90%;
      margin: 0 auto;
      right: 5%;
    }
  }

  .theme--light.v-sheet {
    color: black;
  }
}
</style>

<script>
export default {
  name: "EventSuccessAlert",
  data: () => ({
    showAlert: false
  }),
  props: ["text", "queryParam"],
  mounted: function () {
    if (this.$route.query[this.queryParam] === "true") {
      this.showAlert = true;
      setTimeout(() => (this.showAlert = false), 5000);
    }
  }
};
</script>
