<template>
  <v-alert
      class="mb-5"
      border="right"
      colored-border
      :type="type"
      elevation="2"
      :icon="icon ? icon : icons[type]"
  >
    <slot name="content"></slot>
  </v-alert>
</template>

<script>
export default {
  name: "ColoredBorderAlert",
  props: ["type", "icon"],
  data: () => ({
    icons: {
      warning: "mdi-alert"
    }
  })
};
</script>
