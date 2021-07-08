<template>
  <v-radio :data-test="dataTest" :label="label" :value="value" v-on="on" class="radio">
    <template v-slot:label>
      <slot name="label"/>
    </template>
  </v-radio>
</template>

<style lang="scss">
.radio {
  .theme--light.v-icon {
    color: var(--v-primary-base) !important;
  }
}
</style>

<script>
export default {
  name: "RadioItem",
  props: ["label", "value", "on", "dataTest"]
};
</script>
