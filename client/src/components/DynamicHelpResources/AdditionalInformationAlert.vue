<template>
  <v-alert
      icon="mdi-information-outline"
      class="d-inline-block mb-5"
      elevation="4"
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
  name: "AdditionalInformationAlert",
  props: ["localeTag"]
};
</script>
