<template>
  <div class="linear-box rounded-lg">
    <v-container>
      <v-row>
        <v-col cols="11" md="10" class="mx-auto my-8">
          <slot name="content"></slot>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<style lang="scss" scoped>
.linear-box {
  border: 1px solid var(--v-primary-base);
}
</style>

<script>
export default {
  name: "LinearBox"
};
</script>
