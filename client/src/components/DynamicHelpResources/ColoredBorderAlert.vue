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
    <div v-html="$t(localeTag)"></div>
  </v-alert>
</template>

<script>
// This component contains a slot for static html content,
// and a property for passing the name of locale html content
// Either can be used, or both
export default {
  name: "ColoredBorderAlert",
  props: ["type", "icon", "localeTag"],
  data: () => ({
    icons: {
      info: "mdi-information",
      warning: "mdi-alert",
      error: "mdi-cancel"
    }
  })
};
</script>
