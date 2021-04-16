<template>
  <v-tooltip bottom max-width="220px">
    <template v-slot:activator="{ on, attrs }">
      <v-icon color="secondary" small right v-bind="attrs" v-on="on"
      >mdi-help-circle-outline
      </v-icon
      >
    </template>
    <span>{{ text }}</span>
  </v-tooltip>
</template>

<style lang="scss" scoped>
.v-tooltip__content {
  background: rgba(68, 68, 68, 0.95);
}
</style>

<style lang="scss" scoped>
span {
  white-space: pre-wrap;
}
</style>

<script>
export default {
  name: "QuestionIconTooltip",
  props: ["text"]
};
</script>
