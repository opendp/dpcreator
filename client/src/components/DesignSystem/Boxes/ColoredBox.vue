<template>
  <div class="soft_primary rounded-lg ">
    <v-container>
      <v-row>
        <v-col cols="11" md="10" class="mx-auto my-8">
          <slot name="content"></slot>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
export default {
  name: "ColoredBox"
};
</script>
