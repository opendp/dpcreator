<template>
  <v-checkbox v-on:click="handleCheckboxEvent" :data-test=dataTest v-model="checkboxValue" class="checkbox">
    <template v-slot:label>
      <div
          class="primary--text"
          :class="{ 'ml-2': $vuetify.breakpoint.xsOnly }"
      >
        {{ text }}
      </div>
    </template>
  </v-checkbox>
</template>

<style lang="scss">
.checkbox {
  .mdi-checkbox-blank-outline {
    color: var(--v-primary-base) !important;
  }
}
</style>

<script>
export default {
  name: "Checkbox",
  data: () => ({
    checkboxValue: "false"
  }),
  mounted: function () {
    this.checkboxValue = this.value;
  },
  methods: {
    handleCheckboxEvent() {
      console.log('checkbox event, child')
      this.$emit("click");
    },
  },
  watch: {
    checkboxValue: function (newCheckboxValue) {
      console.log("emitting event hello ")
      this.$emit("update:value", newCheckboxValue);
    }
  },
  props: ["text", "value", "dataTest"]
};
</script>
