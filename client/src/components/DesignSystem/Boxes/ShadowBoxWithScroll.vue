<template>
  <v-card
      class="mb-5 pt-5 pb-2 rounded-lg shadow-card"
      elevation="4"
      :class="{
      'px-3': $vuetify.breakpoint.xsOnly,
      'px-7': $vuetify.breakpoint.smAndUp
    }"
  >
    <v-card-title>
      <slot name="title"></slot>
    </v-card-title>
    <v-card-text>
      <slot name="scrollable-area"></slot>
    </v-card-text>
    <v-card-actions>
      <slot name="actions"></slot>
    </v-card-actions>
  </v-card>
</template>

<style lang="scss" scoped>
.shadow-card {
  border: 1px solid #c2c2c2;
  box-shadow: 2px 2px 6px 0 rgba(0, 0, 0, 0.2);
}
</style>

<script>
export default {
  name: "ShadowBoxWithScroll"
};
</script>
