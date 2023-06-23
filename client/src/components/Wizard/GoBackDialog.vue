<template>
  <v-dialog
          :modelValue="dialog"
          @update:modelValue="dialog = $event"
          :width="$vuetify.breakpoint.smAndDown ? '90%' : '50%'"
  >
    <v-card elevation="2" class="px-10 py-12">
      <v-icon
          style="position: absolute; right: 40px"
          @click="() => $emit('update:dialog', false)"
      >mdi-close
      </v-icon
      >
      <v-card-title>
        <h2 class="title-size-2 mb-5 font-weight-bold">Are you sure?</h2>
      </v-card-title>
      <v-card-text class="text--primary">
        If you move to the previous step, you will lose all the changes made on
        this page.
      </v-card-text>
      <v-card-actions>
        <Button
            color="primary"
            classes="mr-2 px-5"
            :click="() => $emit('confirm')"
            label="Yes"
        />
        <Button
            color="primary"
            outlined
            classes="px-5"
            :click="() => $emit('update:dialog', false)"
            label="Cancel"
        />
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import Button from "../DesignSystem/Button.vue";

export default {
  name: "GoBackDialog",
  components: {Button},
  props: ["dialog"]
};
</script>
