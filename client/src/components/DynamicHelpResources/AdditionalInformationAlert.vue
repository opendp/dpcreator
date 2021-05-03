<template>
  <v-alert
      icon="mdi-information-outline"
      class="d-inline-block mb-5"
      elevation="4"
  >
    <slot name="content"></slot>
  </v-alert>
</template>

<script>
export default {
  name: "AdditionalInformationAlert"
};
</script>
