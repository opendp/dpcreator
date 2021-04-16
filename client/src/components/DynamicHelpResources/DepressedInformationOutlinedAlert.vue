<template>
  <v-alert
      color="grey darken-2"
      outlined
      icon="mdi-information-outline"
      class="d-inline-block mb-5"
  >
    <slot name="content"></slot>
  </v-alert>
</template>

<style lang="scss" scoped>
.v-alert--outlined {
  border-color: rgba(97, 97, 97, 0.5) !important;
}
</style>

<script>
export default {
  name: "DepressedInformationOutlinedAlert"
};
</script>
