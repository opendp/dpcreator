<template>
  <v-btn
      class="button"
      :data-test=dataTest
      :class="classes"
      :color="color"
      :disabled="disabled"
      :type="type"
      @click="handleClick"
      :large="large"
      :small="small"
      :outlined="outlined"
      :width="width"
      :max-width="width"
      :depressed="depressed"
  >
    <slot>{{ label }}</slot>
  </v-btn>
</template>

<style lang="scss">
.button {
  &.v-btn {
    border-radius: 6px !important;
    text-transform: none !important;
    min-width: 170px !important;
    letter-spacing: 0 !important;
    max-width: 400px;
  }

  &.v-btn:not(.v-btn--round).v-size--default {
    height: 42px;
    font-size: 1rem;
  }

  &.v-btn:not(.v-btn--round).v-size--large {
    height: 52px;
  }

  &.v-btn:not(.v-btn--round).v-size--small {
    height: 32px;
  }

  &.theme--light.v-btn.v-btn--disabled.v-btn--has-bg {
    color: white !important;
    background-color: #c2c2c2 !important;
  }
}
</style>

<script>
export default {
  name: "Button",
  props: [
    "classes",
    "color",
    "disabled",
    "type",
    "label",
    "click",
    "url",
    "outlined",
    "large",
    "small",
    "width",
    "depressed",
    "dataTest"
  ],
  methods: {
    handleClick: function () {
      if (this.url) {
        window.location.href = this.url;
      } else {
        if (this.click) {
          this.click();
        }
      }
    }
  }
};
</script>
