<template>
  <v-alert
      class="border-top-alert-dismissible mb-10"
      border="top"
      colored-border
      color="primary"
      elevation="2"
      dismissible
      close-icon="mdi-close"
  >
    <slot name="content"></slot>
  </v-alert>
</template>

<style lang="scss">
.border-top-alert-dismissible {
  .v-alert__dismissible {
    min-width: 0 !important;
    align-self: start;
    top: 15px;
  }
  .v-alert__content p {
    width: 98%;
  }
  .mdi-close {
    color: rgba(0, 0, 0, 0.4) !important;
  }
}
</style>

<script>
export default {
  name: "BorderTopAlertDismissible"
};
</script>
