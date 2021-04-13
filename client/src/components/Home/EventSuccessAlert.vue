<template>
  <v-container class="alert-wrapper">
    <v-alert
        v-model="showAlert"
        type="info"
        icon="mdi-check"
        text
        transition="scale-transition"
        class="alert"
    >
      {{ text }}
    </v-alert>
  </v-container>
</template>

<style lang="scss">
.alert-wrapper {
  position: relative;
}

.alert {
  position: absolute !important;
  top: 0;
  right: 0;
  z-index: 1;

  .v-alert__content,
  .v-icon {
    color: #000000 !important;
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
