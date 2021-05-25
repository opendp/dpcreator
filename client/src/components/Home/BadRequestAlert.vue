<template>
  <v-container
      :class="{
      'mb-5': $vuetify.breakpoint.xsOnly,
      'mb-16': $vuetify.breakpoint.smAndUp
    }"
  >
    <v-row>
      <v-col
          offset-sm="1"
          offset-md="0"
          sm="10"
          class="text-center mx-auto px-5"
          md="7"
      >
        <v-alert
            border="right"
            colored-border
            type="info"
            elevation="2"
            v-show=showAlert>
          {{ alertText }}
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<style lang="scss">
.event-success-alert {
  &.alert-wrapper {
    position: relative;
  }

  .alert {
    position: absolute !important;
    top: 0;
    right: 0;
    z-index: 1;
    @media (max-width: 600px) {
      text-align: center;
      width: 90%;
      margin: 0 auto;
      right: 5%;
    }
  }

  .theme--light.v-sheet {
    color: black;
  }
}
</style>

<script>
export default {
  name: "BadRequestAlert",
  props: ["alertText", "showAlert"],
};
</script>
