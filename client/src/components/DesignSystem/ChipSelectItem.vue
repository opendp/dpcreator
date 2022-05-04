<template>
  <v-chip
      :v-bind="v_bind"
      :input-value="input_value"
      close
      color="blue darken-2"
      text-color="white"
      @click:close="click_close"
  >
    <div data-test="categoryChip"><strong>{{ item }}</strong></div>
  </v-chip>
</template>

<script>
export default {
  name: "ChipSelectItem",
  props: ["v_bind", "input_value", "click", "click_close", "item"]
};
</script>
